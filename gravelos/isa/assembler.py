from typing import Dict, List
from gravelos.core.exceptions import LithicAssemblerError

class LithicAssembler:
    """Translates ASCII Assembly text into 16-bit binaries across two parsing passes."""
    
    OPCODES = {
        "YAWN":0x0, "SCREAM":0x1, "BELLOW":0x2, "ECHO":0x3, "CLANG":0x4, "CRASH":0x5, "SMASH":0x6,
        "HEAVE":0x7, "PULL":0x8, "LEAP":0x9, "STOMP":0xA, "LEAPZ":0xB, "HAUL":0xC, "PLACE":0xD, "SILENCE":0xE,
        "TOSS":0x10, "CATCH":0x11, "INVOKE":0x12, "FLEE":0x13, "CLI":0x14, "STI":0x15, "IRET":0x16
    }
    
    def __init__(self, offset: int = 0x08):
        self.labels: Dict[str, int] = {}
        self.offset = offset  # Memory base location
        
    def _parse_reg(self, t: str) -> int: 
        return int(t.strip(",[] \t")[1:])
        
    def _parse_imm(self, t: str) -> int: 
        s = t.strip(",[] \t")
        return int(s, 16) if s.startswith("0x") else int(s)

    def assemble(self, source: str) -> List[int]:
        self.labels.clear()
        lines = source.split("\n")
        clean_lines =[]
        addr = self.offset
        
        # PASS 1: Calculate structural address lengths and identify label coordinates
        for line in lines:
            line = line.split(";")[0].strip()
            if not line: continue
            if ":" in line:
                lbl, rest = line.split(":", 1)
                self.labels[lbl.strip()] = addr
                if rest.strip(): 
                    clean_lines.append((addr, rest.strip()))
                    addr += 2
            else:
                clean_lines.append((addr, line))
                addr += 2
                
        # PASS 2: Compile logic bounds
        machine_code =[]
        for line_addr, line in clean_lines:
            try:
                parts = [p for p in line.replace(",", " ").split() if p]
                mnemonic = parts[0].upper()
                if mnemonic not in self.OPCODES: raise ValueError(f"Unknown Instruction '{mnemonic}'")
                opcode = self.OPCODES[mnemonic]
                
                # Resolving Opcode Payload Types
                if mnemonic in ["LEAP", "LEAPZ", "INVOKE"]:
                    target = self.labels.get(parts[1], None)
                    if target is None: target = self._parse_imm(parts[1])
                    inst = (opcode << 11) | (target & 0xFF)
                elif mnemonic in ["YAWN", "SILENCE", "FLEE", "CLI", "STI", "IRET"]:
                    inst = (opcode << 11)
                elif mnemonic in ["TOSS", "CATCH"]:
                    rd = self._parse_reg(parts[1])
                    inst = (opcode << 11) | ((rd & 0x7) << 8)
                else:
                    rd, rs1, im_f, im_v = 0, 0, 0, 0
                    if mnemonic in ["SCREAM", "BELLOW", "CLANG", "CRASH", "SMASH", "HEAVE", "PULL"]:
                        rd = self._parse_reg(parts[1])
                        rs1 = self._parse_reg(parts[2])
                        last = parts[3]
                        if last.startswith("R"): im_v = self._parse_reg(last)
                        else: im_f, im_v = 1, self._parse_imm(last) & 0xF
                    elif mnemonic in ["ECHO", "HAUL", "PLACE", "STOMP"]:
                        rs1_or_rd = self._parse_reg(parts[1])
                        if mnemonic == "STOMP": rs1 = rs1_or_rd
                        else: rd = rs1_or_rd
                        
                        last = parts[2]
                        if last.startswith("R"): im_v = self._parse_reg(last)
                        else: im_f, im_v = 1, self._parse_imm(last) & 0xFF # Full 8-bit allowed for address
                        
                    inst = (opcode << 11) | ((rd & 0x7) << 8) | ((rs1 & 0x7) << 5) | ((im_f & 0x1) << 4) | (im_v & 0xFF)
                machine_code.append(inst)
            except Exception as e:
                raise LithicAssemblerError(line_addr, line, str(e))
        return machine_code
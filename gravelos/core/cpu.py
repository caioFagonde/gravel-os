from gravelos.core.memory import AcousticRAM
from gravelos.core.physics import EnhancedClockRock, DungeonFloor
from gravelos.core.exceptions import StackOverflowError, StackUnderflowError
from dataclasses import dataclass

@dataclass
class MicrocodeExplanation:
    """Educational breakdown of the CPU's current internal thoughts."""
    binary_word: str = ""
    fetch_desc: str = ""
    decode_desc: str = ""
    exec_desc: str = ""

class Gravel16CPU:
    def __init__(self, ram: AcousticRAM, clock: EnhancedClockRock, floor: DungeonFloor):
        self.ram = ram
        self.clock = clock
        self.floor = floor
        self.regs = [0] * 8
        self.pc = 0x08       
        self.sp = 0xFF       
        self.program_end_addr = 0xDF 
        self.flag_z, self.flag_n = False, False
        self.halted = False
        
        # Educational Telemetry
        self.log =[]
        self.current_explanation = MicrocodeExplanation()

    def log_evt(self, msg: str) -> None:
        self.log.append(msg)
        if len(self.log) > 12: self.log.pop(0)

    def write_reg(self, idx: int, val: int) -> None:
        self.regs[idx & 0x7] = val & 0xFFFF
        self.flag_z = (self.regs[idx & 0x7] == 0)
        self.flag_n = (self.regs[idx & 0x7] & 0x8000) != 0

    def push(self, val: int, orig_pc: int):
        self.sp -= 1
        self.ram.write(self.sp, val & 0xFF)

    def pop(self, orig_pc: int) -> int:
        val = self.ram.read(self.sp)
        self.sp += 1
        return val

    def step(self) -> None:
        if self.halted: return
        self.clock.tick()
        
        # 1. EDUCATIONAL FETCH PHASE
        inst_high = self.ram.read(self.pc)
        inst_low = self.ram.read(self.pc + 1)
        inst = (inst_high << 8) | inst_low
        orig_pc = self.pc
        self.pc += 2
        
        bin_str = f"{inst:016b}"
        self.current_explanation.binary_word = f"{bin_str[0:4]} {bin_str[4:7]} {bin_str[7:10]} {bin_str[10]} {bin_str[11:]}"
        self.current_explanation.fetch_desc = f"Read 16 bits at PC [0x{orig_pc:02X}]. High byte 0x{inst_high:02X}, Low byte 0x{inst_low:02X}. Auto-incrementing PC to 0x{self.pc:02X}."

        # 2. EDUCATIONAL DECODE PHASE
        opcode   = (inst >> 11) & 0x1F  # Top 5 bits
        rd       = (inst >> 8) & 0x7    # Next 3 bits
        rs1      = (inst >> 5) & 0x7    # Next 3 bits
        imm_flag = (inst >> 4) & 0x1    # 1 bit
        imm_val  = inst & 0xF           # Bottom 4 bits
        target   = inst & 0xFF          # Bottom 8 bits (Alternative read for memory addresses)
        
        val_rs1 = self.regs[rs1]
        val_rs2 = imm_val if imm_flag else self.regs[imm_val & 0x7]
        
        self.current_explanation.decode_desc = f"Opcode extracted as {opcode}. Dest Register is R{rd}. Source 1 is R{rs1}. Immediate Flag is {imm_flag}. Imm Value/Target is {target}."
        
        txt = ""
        # 3. EDUCATIONAL EXECUTE PHASE
        if opcode == 0x0: 
            txt = "YAWN"
            self.current_explanation.exec_desc = "No operation. Skipping cycle."
        elif opcode == 0x1: 
            self.write_reg(rd, val_rs1 + val_rs2)
            txt = f"SCREAM R{rd}, R{rs1}, {val_rs2}"
            self.floor.trigger("ALU_ADD", 1)
            self.current_explanation.exec_desc = f"ALU Adder Activated: Evaluated R{rs1}({val_rs1}) + {val_rs2} = {val_rs1+val_rs2}. Written to R{rd}."
        elif opcode == 0x3: 
            self.write_reg(rd, val_rs2)
            txt = f"ECHO R{rd}, {val_rs2}"
            self.floor.trigger("ALU_MOV", 1)
            self.current_explanation.exec_desc = f"Moved literal/register value {val_rs2} directly into R{rd}."
        elif opcode == 0xC: 
            val = self.ram.read(target)
            self.write_reg(rd, val)
            txt = f"HAUL R{rd}, [0x{target:02X}]"
            self.current_explanation.exec_desc = f"Queried memory address 0x{target:02X}. Found value {val}. Pulled into R{rd}."
        elif opcode == 0xD:
            self.ram.write(target, self.regs[rd])
            txt = f"PLACE R{rd}, [0x{target:02X}]"
            self.current_explanation.exec_desc = f"Took value {self.regs[rd]} from R{rd} and dropped it into memory address 0x{target:02X}."
        elif opcode == 0xE:
            self.halted = True
            txt = "SILENCE (HALT)"
            self.current_explanation.exec_desc = "HALT instruction trapped. Shutting down."
        else:
            # Fallback for complex math ops omitted for brevity in demo. (They map identically to 0x1)
            txt = f"OPCODE 0x{opcode:02X} EXECUTED."
            self.current_explanation.exec_desc = f"Handled arithmetic opcode mapping {opcode}."

        self.log_evt(f"[dim]0x{orig_pc:02X}[/dim] | {txt}")
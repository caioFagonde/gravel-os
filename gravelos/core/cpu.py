from gravelos.core.memory import AcousticRAM
from gravelos.core.physics import EnhancedClockRock, DungeonFloor
from gravelos.core.exceptions import StackOverflowError, StackUnderflowError
import time

class Gravel16CPU:
    """
    The Virtual Von Neumann core. It runs Fetch, Decode, Execute per tick.
    """
    def __init__(self, ram: AcousticRAM, clock: EnhancedClockRock, floor: DungeonFloor):
        self.ram = ram
        self.clock = clock
        self.floor = floor
        
        self.regs = [0] * 8
        self.pc = 0x08       # Boot logic avoids 0x00 IVT bounds.
        self.sp = 0xFF       # The Stack grows down from roof.
        self.program_end_addr = 0xDF 
        
        self.flag_z = False
        self.flag_n = False
        self.halted = False
        
        # Hardware interrupt vars
        self.interrupts_enabled = True
        self.pending_irq = None
        self.in_isr = False
        
        self.log =[]

    def log_evt(self, msg: str) -> None:
        self.log.append(msg)
        if len(self.log) > 12: self.log.pop(0)

    def write_reg(self, idx: int, val: int) -> None:
        self.regs[idx & 0x7] = val & 0xFFFF
        self.flag_z = (self.regs[idx & 0x7] == 0)
        self.flag_n = (self.regs[idx & 0x7] & 0x8000) != 0

    def trigger_irq(self, num: int):
        if self.pending_irq is None:
            self.pending_irq = num

    def push(self, val: int, orig_pc: int):
        self.sp -= 1
        self.ram.write(self.sp, val & 0xFF)
        if self.sp < self.program_end_addr:
            raise StackOverflowError(self.sp, orig_pc)

    def pop(self, orig_pc: int) -> int:
        if self.sp >= 0xFF:
            raise StackUnderflowError(self.sp, orig_pc)
        val = self.ram.read(self.sp)
        self.sp += 1
        return val

    def step(self) -> None:
        """The fundamental Fetch-Decode-Execute pipeline."""
        if self.halted: return
            
        # Tick the master clock oscillator (forces degradation evaluation)
        self.clock.tick()
        
        # PRE-FETCH: Check Hardware Vectors
        if self.pending_irq is not None and self.interrupts_enabled and not self.in_isr:
            orig_pc = self.pc
            self.push(self.pc & 0xFF, orig_pc) # Push return address
            for r in range(8): self.push(self.regs[r] & 0xFF, orig_pc) # Push registers
            
            # Read IVT Address
            ivt_base = self.pending_irq * 2
            isr_addr = (self.ram.read(ivt_base) << 8) | self.ram.read(ivt_base + 1)
            
            self.pc = isr_addr & 0xFF
            self.in_isr = True
            self.pending_irq = None
            self.log_evt(f"🔴 TRAP TO ISR: PC={self.pc:02X}")

        # 1. FETCH
        inst = (self.ram.read(self.pc) << 8) | self.ram.read(self.pc + 1)
        orig_pc = self.pc
        self.pc += 2
        
        # 2. DECODE
        opcode   = (inst >> 11) & 0x1F
        rd       = (inst >> 8) & 0x7
        rs1      = (inst >> 5) & 0x7
        imm_flag = (inst >> 4) & 0x1
        imm_val  = inst & 0xF
        target   = inst & 0xFF
        
        val_rs1 = self.regs[rs1]
        val_rs2 = imm_val if imm_flag else self.regs[imm_val & 0x7]
        
        txt = ""
        # 3. EXECUTE
        if opcode == 0x0: txt = "YAWN"
        elif opcode == 0x1: self.write_reg(rd, val_rs1 + val_rs2); txt = f"SCREAM R{rd}, R{rs1}, {val_rs2}"; self.floor.trigger("ALU_ADD", 1)
        elif opcode == 0x2: self.write_reg(rd, val_rs1 - val_rs2); txt = f"BELLOW R{rd}, R{rs1}, {val_rs2}"; self.floor.trigger("ALU_SUB", 1)
        elif opcode == 0x3: self.write_reg(rd, val_rs2); txt = f"ECHO R{rd}, {val_rs2}"; self.floor.trigger("ALU_MOV", 1)
        elif opcode == 0x4: self.write_reg(rd, val_rs1 & val_rs2); txt = f"CLANG R{rd}"
        elif opcode == 0x5: self.write_reg(rd, val_rs1 | val_rs2); txt = f"CRASH R{rd}"
        elif opcode == 0x6: self.write_reg(rd, val_rs1 ^ val_rs2); txt = f"SMASH R{rd}"
        elif opcode == 0x7: self.write_reg(rd, val_rs1 << val_rs2); txt = f"HEAVE R{rd}"
        elif opcode == 0x8: self.write_reg(rd, val_rs1 >> val_rs2); txt = f"PULL R{rd}"
        elif opcode == 0x9: self.pc = target; txt = f"LEAP 0x{target:02X}"
        elif opcode == 0xA: 
            res = val_rs1 - val_rs2
            self.flag_z, self.flag_n = (res == 0), (res < 0)
            txt = f"STOMP R{rs1}, {val_rs2}"
        elif opcode == 0xB: 
            if self.flag_z: self.pc = target
            txt = f"LEAPZ 0x{target:02X}"
        elif opcode == 0xC: 
            self.write_reg(rd, self.ram.read(val_rs2 & 0xFF))
            txt = f"HAUL R{rd}, [0x{val_rs2:02X}]"
        elif opcode == 0xD:
            self.ram.write(val_rs2 & 0xFF, self.regs[rd])
            txt = f"PLACE R{rd}, [0x{val_rs2:02X}]"
        elif opcode == 0xE:
            self.halted = True; txt = "SILENCE (HALT)"
            
        # STACK & ISR OPCODES
        elif opcode == 0x10: self.push(self.regs[rd], orig_pc); txt = f"TOSS R{rd}"
        elif opcode == 0x11: self.write_reg(rd, self.pop(orig_pc)); txt = f"CATCH R{rd}"
        elif opcode == 0x12: self.push(self.pc & 0xFF, orig_pc); self.pc = target; txt = f"INVOKE 0x{target:02X}"
        elif opcode == 0x13: self.pc = self.pop(orig_pc); txt = "FLEE"
        elif opcode == 0x14: self.interrupts_enabled = False; txt = "CLI (MASK ON)"
        elif opcode == 0x15: self.interrupts_enabled = True; txt = "STI (MASK OFF)"
        elif opcode == 0x16: # IRET
            for r in reversed(range(8)): self.write_reg(r, self.pop(orig_pc))
            self.pc = self.pop(orig_pc)
            self.in_isr = False
            txt = f"IRET (Unwound to 0x{self.pc:02X})"
        else:
            self.halted = True
            txt = f"ILLEGAL OPCODE 0x{opcode:02X}"
            
        self.log_evt(f"[dim]0x{orig_pc:02X}[/dim] | {txt}")
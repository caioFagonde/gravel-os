from typing import Dict, List, Optional
from gravelos.compiler.parser import ASTNode, Program, Assign, BinOp, Num, Var
from gravelos.core.exceptions import RegisterExhaustionError

# Mapping abstract syntax math into our 16-bit Assembly ISA
OP_TO_MNEMONIC = {
    '+': 'SCREAM', '-': 'BELLOW', '&': 'CLANG', '|': 'CRASH', '^': 'SMASH',
    '<<': 'HEAVE', '>>': 'PULL'
}

# Python transpilation targets
OP_TO_PYTHON = {
    '+': '+', '-': '-', '&': '&', '|': '|', '^': '^', '<<': '<<', '>>': '>>'
}

class EducationalCodeGenerator:
    """
    Takes an Abstract Syntax Tree (AST) and lowers it to Machine Architecture.
    Unlike standard compilers, this one narrates its decisions for the student.
    """
    def __init__(self):
        self.instructions: List[str] = []
        self.educational_log: List[str] =[] 
        self.free_registers = [f"R{i}" for i in reversed(range(8))] 
        self.symbol_table: Dict[str, int] = {}
        self.next_vram_address = 0x10  
        self.max_stack_depth = 0

    def alloc_reg(self, reason: str) -> str:
        if not self.free_registers: 
            self.educational_log.append("[red]ERROR: AST too deep! Register Spill required.[/red]")
            raise RegisterExhaustionError()
        reg = self.free_registers.pop()
        current_used = 8 - len(self.free_registers)
        if current_used > self.max_stack_depth:
            self.max_stack_depth = current_used
        self.educational_log.append(f"  [dim]Allocated {reg} (Reason: {reason})[/dim]")
        return reg

    def free_reg(self, reg: str):
        if reg not in self.free_registers: 
            self.free_registers.append(reg)
            self.educational_log.append(f"  [dim]Freed {reg} back to the pool.[/dim]")

    def emit(self, inst: str, educational_comment: str):
        padded_inst = inst.ljust(25)
        self.instructions.append(f"{padded_inst} ; [LEARN] {educational_comment}")

    def generate_lithic_asm(self, node: Program) -> tuple[str, str]:
        self.educational_log.append("[bold cyan]Phase 1: Beginning Code Generation (AST Traversal)[/bold cyan]")
        self.instructions = ["; --- LITHIC-ASM TARGET WITH EDUCATIONAL SYMBOLS ---"]
        
        for stmt in node.statements:
            self.educational_log.append(f"\n[bold yellow]Visiting Node: {type(stmt).__name__}[/bold yellow]")
            self.instructions.append(f"\n; Resolving: {type(stmt).__name__}")
            result_reg = self.visit(stmt)
            if result_reg: 
                self.free_reg(result_reg)
                
        self.emit("SILENCE", "HALT opcode. Shuts down the CPU metronome.")
        self.educational_log.append(f"\n[bold green]Success![/bold green] Maximum simultaneous registers utilized: {self.max_stack_depth}/8")
        
        return "\n".join(self.instructions), "\n".join(self.educational_log)

    def visit(self, node: ASTNode) -> Optional[str]:
        meth = getattr(self, f'visit_{type(node).__name__}')
        return meth(node)

    def visit_Assign(self, node: Assign) -> Optional[str]:
        val_reg = self.visit(node.expr)
        if node.name == "VRAM_TARGET":
            addr = 0xF0
            comment = f"Memory-mapped hardware pointer directly targets Address 0xF0"
        else:
            if node.name not in self.symbol_table:
                self.symbol_table[node.name] = self.next_vram_address
                self.next_vram_address += 2
            addr = self.symbol_table[node.name]
            comment = f"Store evaluated variable '{node.name}' to heap RAM"
            
        self.emit(f"PLACE {val_reg}, [0x{addr:02X}]", comment)
        self.free_reg(val_reg)
        return None

    def visit_BinOp(self, node: BinOp) -> str:
        self.educational_log.append("  Resolving Left child...")
        left_reg = self.visit(node.left)
        self.educational_log.append("  Resolving Right child...")
        right_reg = self.visit(node.right)
        
        mnem = OP_TO_MNEMONIC[node.op]
        self.emit(f"{mnem} {left_reg}, {left_reg}, {right_reg}", f"ALU evaluates {node.op} on {left_reg} and {right_reg}. Overwrites {left_reg}.")
        self.free_reg(right_reg)
        return left_reg

    def visit_Num(self, node: Num) -> str:
        reg = self.alloc_reg(f"Holding integer {node.value}")
        self.emit(f"ECHO {reg}, {node.value}", f"Load immediate integer into {reg}")
        return reg

    def visit_Var(self, node: Var) -> str:
        reg = self.alloc_reg(f"Loading variable '{node.name}'")
        if node.name == "VRAM_TARGET":
            addr = 0xF0
        else:
            if node.name not in self.symbol_table:
                self.symbol_table[node.name] = self.next_vram_address
                self.next_vram_address += 2
                self.emit(f"ECHO {reg}, 0", f"Implicit void initialization for undeclared var '{node.name}'")
            addr = self.symbol_table[node.name]
            
        self.emit(f"HAUL {reg}, [0x{addr:02X}]", f"Fetch 16-bit word from memory pointer for '{node.name}'")
        return reg

    def generate_python(self, node: Program) -> str:
        """Translating RUNE AST into Python 3.x Source Code."""
        output = ["# === GRAVELOS EDUCATIONAL TRANSPILER ==="]
        output.append("# Translating RUNE AST into Python 3.x Source Code\n")
        
        for stmt in node.statements:
            if isinstance(stmt, Assign):
                val_str = self._transpile_expr(stmt.expr)
                output.append(f"{stmt.name} = {val_str}")
        return "\n".join(output)
        
    def _transpile_expr(self, node: ASTNode) -> str:
        if isinstance(node, Num): return str(node.value)
        elif isinstance(node, Var): return node.name
        elif isinstance(node, BinOp):
            l = self._transpile_expr(node.left)
            r = self._transpile_expr(node.right)
            py_op = OP_TO_PYTHON[node.op]
            return f"({l} {py_op} {r})"
        return "UNKNOWN"

    def generate_rock_instructions(self, node: Program, machine_code: List[int]) -> str:
        """
        Transpiles the software directly into a physical setup manual.
        This explicitly demonstrates how semantic AST commands and 
        compiled machine code manifest in bare-metal reality.
        """
        output = ["[bold cyan]=== PHYSICAL LITHIC DEPLOYMENT MANUAL ===[/bold cyan]"]
        output.append("A Wizard's guide to translating compiled software into a literal hardware layout.\n")
        
        output.append("[bold yellow]PHASE 1: THE SEMANTIC RITUAL (AST Translation)[/bold yellow]")
        output.append("[dim]This translates high-level semantic intent into literal physical actions.[/dim]")
        step_idx = 1
        
        # Traverse AST for physical meaning
        for stmt in node.statements:
            if isinstance(stmt, Assign):
                output.append(f"\n[bold white]Step {step_idx}. Variable Assignment ({stmt.name})[/bold white]")
                output.append(f"   - Grab an empty D-Flip-Flop memory rock. Paint the rune '{stmt.name}' on it.")
                output.append(f"   - Set the rock on the ground. Wait for the ALU result to propagate acoustically.")
                output.append(f"   - When heard, strike it with a tuning fork to lock its acoustic state.")
            elif isinstance(stmt, Num):
                output.append(f"\n[bold white]Step {step_idx}. Immediate Value Encoding ({stmt.value})[/bold white]")
                output.append(f"   - Scoop up a cluster of 16 empty pebbles (a physical CPU Register).")
                output.append(f"   - Enchant them to constantly vibrate at the harmonic harmonic matching {stmt.value}.")
            elif isinstance(stmt, BinOp):
                op_boulder = {"+": "ADD (SCREAM)", "-": "SUB (BELLOW)", "&": "AND (CLANG)", "|": "OR (CRASH)", "^": "XOR (SMASH)", "<<": "L-SHIFT (HEAVE)", ">>": "R-SHIFT (PULL)"}.get(stmt.op, "UNKNOWN")
                output.append(f"\n[bold white]Step {step_idx}. Physical ALU Execution ({stmt.op})[/bold white]")
                output.append(f"   - Carry your two input register pebble-clusters toward the central {op_boulder} Boulder.")
                output.append(f"   - Set the pebbles on the ground facing the gate. Step back.")
                output.append(f"   - The Boulder will process their combined acoustics and scream the result.")
            step_idx += 1
            
        output.append("\n\n[bold yellow]PHASE 2: BARE-METAL BOOTLOADER SEQUENCE (Memory Scribing)[/bold yellow]")
        output.append("[dim]Before turning the machine on, you must manually toggle the state of physical RAM stones to flash the binary executable.[/dim]")
        
        # Output exact 16-bit bare metal arrays
        addr = 0x08
        for word in machine_code:
            bin_str = f"{word:016b}"
            chant = " ".join(["[bold green]BING[/]" if b=="1" else "[dim red]BONG[/]" for b in bin_str])
            output.append(f"\n[bold magenta]Go to Dungeon Coordinates (Address 0x{addr:02X})[/bold magenta]")
            output.append("   - Locate the row of 16 memory pebbles embedded in the floor here.")
            output.append("   - Tap them left-to-right to enforce the following states:")
            output.append(f"   {chant}")
            addr += 2
            
        output.append("\n[bold red]PHASE 3: IGNITION[/bold red]")
        output.append("   - Strike the MASTER_CLK oscillator rock heavily with a warhammer.")
        output.append("   - The software will immediately begin execution at the speed of sound.")
        
        return "\n".join(output)
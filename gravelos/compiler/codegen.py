from typing import Dict, List, Optional
from gravelos.compiler.parser import ASTNode, Program, Assign, BinOp, Num, Var
from gravelos.core.exceptions import RegisterExhaustionError

# Mapping abstract syntax math into our 16-bit Assembly ISA
OP_TO_MNEMONIC = {
    '+': 'SCREAM', '-': 'BELLOW', '&': 'CLANG', '|': 'CRASH', '^': 'SMASH',
    '<<': 'HEAVE', '>>': 'PULL'
}

# Python transpilation targets (For educational Transpiler demonstration)
OP_TO_PYTHON = {
    '+': '+', '-': '-', '&': '&', '|': '|', '^': '^', '<<': '<<', '>>': '>>'
}

class EducationalCodeGenerator:
    """
    Takes an Abstract Syntax Tree (AST) and lowers it to Machine Architecture.
    Unlike standard compilers, this one narrates its decisions for the student.
    """
    def __init__(self):
        self.instructions: List[str] =[]
        self.educational_log: List[str] =[] # Tracks the "why" of compiler decisions
        self.free_registers = [f"R{i}" for i in reversed(range(8))] # R7 down to R0
        self.symbol_table: Dict[str, int] = {}
        self.next_vram_address = 0x10  # User memory starts here to avoid IVT
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
        """Emits assembly with DWARF-style educational comments"""
        # Padding to make assembly line up beautifully
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

    # ---- VISITOR PATTERN IMPLEMENTATIONS ----

    def visit(self, node: ASTNode) -> Optional[str]:
        meth = getattr(self, f'visit_{type(node).__name__}')
        return meth(node)

    def visit_Assign(self, node: Assign) -> Optional[str]:
        # 1. Evaluate the expression first
        val_reg = self.visit(node.expr)
        
        # 2. Assign memory address mapping
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
                # To prevent compiler crash on undefined vars, auto-init to 0
                self.symbol_table[node.name] = self.next_vram_address
                self.next_vram_address += 2
                self.emit(f"ECHO {reg}, 0", f"Implicit void initialization for undeclared var '{node.name}'")
            addr = self.symbol_table[node.name]
            
        self.emit(f"HAUL {reg}, [0x{addr:02X}]", f"Fetch 16-bit word from memory pointer for '{node.name}'")
        return reg

    # ---- EDUCATIONAL TRANSPILER DEMO ----
    def generate_python(self, node: Program) -> str:
        """
        Instead of targeting Assembly, target High-Level Python!
        This teaches the user the difference between a Compiler and Transpiler.
        """
        output = ["# === GRAVELOS EDUCATIONAL TRANSPILER ==="]
        output.append("# Translating RUNE AST into Python 3.x Source Code\n")
        
        for stmt in node.statements:
            if isinstance(stmt, Assign):
                val_str = self._transpile_expr(stmt.expr)
                output.append(f"{stmt.name} = {val_str}")
        return "\n".join(output)
        
    def _transpile_expr(self, node: ASTNode) -> str:
        if isinstance(node, Num):
            return str(node.value)
        elif isinstance(node, Var):
            return node.name
        elif isinstance(node, BinOp):
            l = self._transpile_expr(node.left)
            r = self._transpile_expr(node.right)
            py_op = OP_TO_PYTHON[node.op]
            return f"({l} {py_op} {r})"
        return "UNKNOWN"
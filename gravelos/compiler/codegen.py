from typing import Dict, List, Optional
from gravelos.compiler.parser import ASTNode, Program, Assign, BinOp, Num, Var
from gravelos.core.exceptions import RegisterExhaustionError

OP_TO_MNEMONIC = {
    '+': 'SCREAM', '-': 'BELLOW', '&': 'CLANG', '|': 'CRASH', '^': 'SMASH',
    '<<': 'HEAVE', '>>': 'PULL'
}

class CodeGenerator:
    """Takes validated Abstract Syntax Graphs and creates screaming logic boundaries."""
    def __init__(self):
        self.instructions: List[str] =[]
        self.free_registers = [f"R{i}" for i in reversed(range(8))]
        self.symbol_table: Dict[str, int] = {}
        self.next_vram_address = 0x10  # Starting heap offset

    def alloc_reg(self) -> str:
        if not self.free_registers: raise RegisterExhaustionError()
        return self.free_registers.pop()

    def free_reg(self, reg: str):
        if reg not in self.free_registers: self.free_registers.append(reg)

    def generate(self, node: Program) -> str:
        self.instructions = ["; --- COMPILED BY GRAVELOS RUNE COMPILER ---"]
        for stmt in node.statements:
            self.instructions.append(f"; {type(stmt).__name__} Logic Path")
            r = self.visit(stmt)
            if r: self.free_reg(r)
        self.instructions.append("SILENCE\n")
        return "\n".join(self.instructions)

    def visit(self, node: ASTNode) -> Optional[str]:
        meth = getattr(self, f'visit_{type(node).__name__}')
        return meth(node)

    def visit_Assign(self, node: Assign) -> Optional[str]:
        v_reg = self.visit(node.expr)
        # Check specific Memory-Mapped Variable Bindings
        if node.name == "VRAM_TARGET":
            addr = 0xF0
        elif node.name == "PADDLE_PTR":
            addr = 0xF1
        else:
            if node.name not in self.symbol_table:
                self.symbol_table[node.name] = self.next_vram_address
                self.next_vram_address += 2
            addr = self.symbol_table[node.name]
            
        self.instructions.append(f"PLACE {v_reg}, [0x{addr:02X}]")
        self.free_reg(v_reg)
        return None

    def visit_BinOp(self, node: BinOp) -> str:
        l_reg = self.visit(node.left)
        r_reg = self.visit(node.right)
        mnem = OP_TO_MNEMONIC[node.op]
        self.instructions.append(f"{mnem} {l_reg}, {l_reg}, {r_reg}")
        self.free_reg(r_reg)
        return l_reg

    def visit_Num(self, node: Num) -> str:
        r = self.alloc_reg()
        self.instructions.append(f"ECHO {r}, {node.value}")
        return r

    def visit_Var(self, node: Var) -> str:
        r = self.alloc_reg()
        # Direct Memory map fetcher bindings
        if node.name == "VRAM_TARGET":
            addr = 0xF0
        else:
            if node.name not in self.symbol_table:
                self.symbol_table[node.name] = self.next_vram_address
                self.next_vram_address += 2
                self.instructions.append(f"ECHO {r}, 0 ; init void pointer")
            addr = self.symbol_table[node.name]
            
        self.instructions.append(f"HAUL {r}, [0x{addr:02X}]")
        return r
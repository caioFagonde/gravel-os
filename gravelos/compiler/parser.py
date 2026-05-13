from dataclasses import dataclass
from typing import List, Optional
from rich.tree import Tree
from gravelos.compiler.lexer import Token
from gravelos.core.exceptions import ParseException

class ASTNode:
    def to_rich_tree(self) -> Tree: raise NotImplementedError

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    def to_rich_tree(self) -> Tree:
        t = Tree("[bold cyan]AST Root (Program)[/]")
        for s in self.statements: t.add(s.to_rich_tree())
        return t

@dataclass
class Assign(ASTNode):
    name: str
    expr: ASTNode
    def to_rich_tree(self) -> Tree:
        t = Tree(f"[bold magenta]Assign[/]: [green]{self.name}[/]")
        t.add(self.expr.to_rich_tree())
        return t

@dataclass
class BinOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode
    def to_rich_tree(self) -> Tree:
        c = "red" if self.op in ["+", "-"] else ("magenta" if self.op in ["<<", ">>"] else "yellow")
        t = Tree(f"[{c}]BinOp '{self.op}'[/]")
        t.add(self.left.to_rich_tree())
        t.add(self.right.to_rich_tree())
        return t

@dataclass
class Num(ASTNode):
    value: int
    def to_rich_tree(self) -> Tree: return Tree(f"[blue]Num:[/] {self.value}")

@dataclass
class Var(ASTNode):
    name: str
    def to_rich_tree(self) -> Tree: return Tree(f"[green]Var:[/] {self.name}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens): self.current = self.tokens[self.pos]

    def match(self, t_type: str) -> bool:
        if self.current.type == t_type:
            self.advance()
            return True
        return False

    def parse(self) -> Program:
        stmts =[]
        while self.current.type != 'EOF':
            if self.current.type == 'NEWLINE':
                self.advance()
                continue
            stmts.append(self.parse_statement())
        return Program(stmts)

    def parse_statement(self) -> ASTNode:
        if self.current.type == 'KEYWORD' and self.current.value == 'let':
            self.advance()
            if self.current.type != 'IDENTIFIER':
                raise ParseException("Expected variable identifier", self.current.line)
            name = self.current.value
            self.advance()
            if not self.match('ASSIGN'):
                raise ParseException("Expected '=' in assignment", self.current.line)
            return Assign(name, self.parse_expr())
        elif self.current.type == 'IDENTIFIER' and self.tokens[self.pos+1].type == 'ASSIGN':
            name = self.current.value
            self.advance(); self.advance()
            return Assign(name, self.parse_expr())
        return self.parse_expr()

    def parse_expr(self) -> ASTNode:
        node = self.parse_term()
        while self.current.type in ('OPERATOR', 'LSHIFT', 'RSHIFT'):
            op = self.current.value
            self.advance()
            node = BinOp(left=node, op=op, right=self.parse_term())
        return node

    def parse_term(self) -> ASTNode:
        if self.current.type == 'NUMBER':
            v = int(self.current.value); self.advance(); return Num(v)
        elif self.current.type == 'IDENTIFIER':
            n = self.current.value; self.advance(); return Var(n)
        elif self.current.type == 'LPAREN':
            self.advance()
            node = self.parse_expr()
            if not self.match('RPAREN'): raise ParseException("Missing closing parenthesis", self.current.line)
            return node
        raise ParseException(f"Unexpected structural fault: {self.current.value}", self.current.line)
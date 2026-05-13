import re
from dataclasses import dataclass
from typing import List
from gravelos.core.exceptions import ParseException

@dataclass
class Token:
    type: str
    value: str
    line: int

# We strictly evaluate Lexical syntax limits
TOKEN_SPEC = [
    ('KEYWORD',  r'\blet\b|\bwhile\b'), # Expanded to prep for While Loops
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('NUMBER',   r'\d+'),
    ('ASSIGN',   r'='),
    ('LSHIFT',   r'<<'),
    ('RSHIFT',   r'>>'),
    ('OPERATOR', r'[+\-&|^]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('NEWLINE',  r'\n'),
    ('COMMENT',  r'#[^\n]*'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]
TOKEN_REGEX = re.compile('|'.join(f'(?P<{p[0]}>{p[1]})' for p in TOKEN_SPEC))

def tokenize(code: str) -> List[Token]:
    tokens =[]
    line_num = 1
    for match in TOKEN_REGEX.finditer(code):
        kind = match.lastgroup
        value = match.group(kind)
        
        if kind == 'NEWLINE':
            line_num += 1
            tokens.append(Token(kind, value, line_num))
        elif kind in ('SKIP', 'COMMENT'):
            continue
        elif kind == 'MISMATCH':
            raise ParseException(f"Arcane Glyphs unintelligible: '{value}'", line_num)
        else:
            tokens.append(Token(kind, value, line_num))
            
    tokens.append(Token('EOF', '', line_num))
    return tokens
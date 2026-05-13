from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Header, Footer, TextArea, RichLog, TabbedContent, TabPane
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.table import Table

from gravelos.compiler.lexer import tokenize
from gravelos.compiler.parser import Parser
from gravelos.compiler.codegen import EducationalCodeGenerator
from gravelos.isa.assembler import LithicAssembler
from gravelos.core.exceptions import RegisterExhaustionError, ParseException

class EducationalRuneIDE(App):
    CSS = """
    Screen { layout: grid; grid-size: 2 1; grid-columns: 1fr 1fr; }
    #editor-panel { height: 100%; border: heavy #00aa00; background: $boost; }
    #tabs { height: 100%; border: heavy #00aaaa; }
    """
    TITLE = "RUNE Compiler & Educational Transpiler"
    SUB_TITLE = "Learn Compiler Architecture through Screaming Rocks"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        initial_code = "# Compute Pythagorean rough distance\nlet a = 12\nlet b = 5\nlet a_sq = a + a # demo simplified math\nlet b_sq = b + b\nVRAM_TARGET = a_sq + b_sq\n"
        
        yield TextArea(initial_code, language="python", id="editor-panel")
        
        with TabbedContent(id="tabs"):
            with TabPane("1. Lexer (Tokens)"):
                yield RichLog(id="log-lexer", markup=True)
            with TabPane("2. Parser (AST)"):
                yield RichLog(id="log-ast", markup=True)
            with TabPane("3. CodeGen / Registers"):
                yield RichLog(id="log-alloc", markup=True)
            with TabPane("4. Target: LITHIC Assembly"):
                yield RichLog(id="log-asm", markup=True)
            with TabPane("5. Target: Python Code"):
                yield RichLog(id="log-transpiled", markup=True)
            with TabPane("6. Target: Physical Rocks"):
                yield RichLog(id="log-rocks", markup=True)
                
        yield Footer()

    @on(TextArea.Changed, "#editor-panel")
    def run_compilation_pipeline(self, event: TextArea.Changed) -> None:
        source = event.text_area.text
        if not source.strip(): return

        logs = {
            "lexer": self.query_one("#log-lexer", RichLog),
            "ast": self.query_one("#log-ast", RichLog),
            "alloc": self.query_one("#log-alloc", RichLog),
            "asm": self.query_one("#log-asm", RichLog),
            "transpiled": self.query_one("#log-transpiled", RichLog),
            "rocks": self.query_one("#log-rocks", RichLog),
        }
        for log in logs.values(): log.clear()

        try:
            # Phase 1: LEXICAL ANALYSIS
            tokens = tokenize(source)
            t_table = Table("Type", "Value", "Line", box=box.MINIMAL)
            for t in tokens: t_table.add_row(f"[cyan]{t.type}[/]", f"[green]{t.value}[/]", str(t.line))
            logs["lexer"].write(Panel(t_table, title="Lexical Token Stream", subtitle="Converting string characters into meaning"))

            # Phase 2: PARSER (AST)
            ast_root = Parser(tokens).parse()
            logs["ast"].write(Panel(ast_root.to_rich_tree(), title="Abstract Syntax Tree", subtitle="Understanding operator precedence and math order"))

            # Phase 3: CODEGEN & REGISTER ALLOCATION
            codegen = EducationalCodeGenerator()
            lithic_asm, allocation_narrative = codegen.generate_lithic_asm(ast_root)
            logs["alloc"].write(Panel(allocation_narrative, title="Compiler Internal Monologue"))
            
            asm_fmt = lithic_asm.replace("SCREAM", "[red]SCREAM[/]").replace("ECHO", "[green]ECHO[/]").replace("PLACE", "[magenta]PLACE[/]").replace("; [LEARN]", "[dim yellow];[/dim yellow]")
            logs["asm"].write(Panel(Text.from_markup(asm_fmt), title="Generated Machine Assembly", subtitle="Annotated with DWARF-style educational comments"))

            # Phase 4: PYTHON TRANSPILER TARGET
            python_code = codegen.generate_python(ast_root)
            logs["transpiled"].write(Panel(f"[bold green]{python_code}[/]", title="Transpiled Output (Target: Python 3)", subtitle="Demonstrating a backend swapping AST out to a high-level language!"))

            # Phase 5: PHYSICAL ROCK TRANSPILER TARGET
            machine_code = LithicAssembler(offset=0x08).assemble(lithic_asm)
            rock_manual = codegen.generate_rock_instructions(ast_root, machine_code)
            logs["rocks"].write(Panel(Text.from_markup(rock_manual), title="Physical Lithic Substrate Instructions", subtitle="The literal instructions to run this program in reality."))

        except Exception as e:
            # Broadcast the error visually so the student knows EXACTLY what caused the logic breakdown
            error_art = f"[bold red]CATASTROPHIC COMPILER ERROR[/bold red]\n\n[yellow]{str(e)}[/yellow]"
            for log in logs.values():
                log.write(Panel(error_art, border_style="red", box=box.ROUNDED))
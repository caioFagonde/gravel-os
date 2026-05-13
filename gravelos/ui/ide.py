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
            with TabPane("2. Parser (AST Tree)"):
                yield RichLog(id="log-ast", markup=True)
            with TabPane("3. Register Allocator"):
                yield RichLog(id="log-alloc", markup=True)
            with TabPane("4. LITHIC Assembly"):
                yield RichLog(id="log-asm", markup=True)
            with TabPane("5. Transpiler Target"):
                yield RichLog(id="log-transpiled", markup=True)
                
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

            # Phase 4: TRANSPILER TARGET (Source to Source mapping)
            python_code = EducationalCodeGenerator().generate_python(ast_root)
            logs["transpiled"].write(Panel(f"[bold green]{python_code}[/]", title="Transpiled Output (Target: Python 3)", subtitle="Demonstrating a backend swapping AST out to high level language!"))

        except Exception as e:
            # Print exceptions across all active panes so the user isn't confused why it broke
            error_art = f"[bold red]CATASTROPHIC COMPILER ERROR[/bold red]\n\n[yellow]{str(e)}[/yellow]"
            for log in logs.values():
                log.write(Panel(error_art, border_style="red", box=box.ROUNDED))
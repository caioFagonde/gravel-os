from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Header, Footer, TextArea, RichLog
from rich.panel import Panel
from rich.text import Text
from rich import box
from gravelos.compiler.lexer import tokenize
from gravelos.compiler.parser import Parser
from gravelos.compiler.codegen import CodeGenerator
from gravelos.core.exceptions import RegisterExhaustionError, ParseException

class RuneCompilerIDE(App):
    CSS = """
    Screen { layout: grid; grid-size: 2 2; grid-columns: 1fr 1fr; grid-rows: 1fr 1fr; }
    #editor-panel { row-span: 2; height: 100%; border: heavy #00aa00; background: $boost; }
    #ast-log { height: 100%; border: heavy #aaaa00; }
    #asm-log { height: 100%; border: heavy #00aaaa; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        # Pass basic template program to avoid starting empty.
        initial = "let x = 10\nlet y = x + 5\nVRAM_TARGET = y\n"
        yield TextArea(initial, language="python", id="editor-panel")
        yield RichLog(id="ast-log", markup=True)
        yield RichLog(id="asm-log", markup=True)
        yield Footer()

    @on(TextArea.Changed, "#editor-panel")
    def trigger_compile(self, event: TextArea.Changed) -> None:
        ast_log = self.query_one("#ast-log", RichLog)
        asm_log = self.query_one("#asm-log", RichLog)
        
        source = event.text_area.text
        if not source.strip():
            ast_log.clear(); asm_log.clear(); return

        try:
            tokens = tokenize(source)
            ast = Parser(tokens).parse()
            asm = CodeGenerator().generate(ast)

            ast_log.clear(); asm_log.clear()
            ast_log.write(Panel("[bold green]SUCCESS: PARSED[/]", box=box.MINIMAL))
            ast_log.write(ast.to_rich_tree())
            
            # Write ASM target 
            asm_fmt = asm.replace("SCREAM", "[red]SCREAM[/]").replace("ECHO", "[green]ECHO[/]").replace("PLACE", "[magenta]PLACE[/]")
            asm_log.write(Panel("[bold cyan]LITHIC-ASM TARGET[/]", box=box.MINIMAL))
            asm_log.write(Text.from_markup(asm_fmt))
            
        except RegisterExhaustionError:
            ast_log.clear(); asm_log.clear()
            ast_log.write(Panel("[red]FATAL: REGISTER SPILL (MAX AST DEPTH EXCEEDED). NOT ENOUGH ROCKS![/red]"))
        except ParseException as e:
            ast_log.clear(); asm_log.clear()
            goblin = f"SYNTAX ERROR!\n\n  \\o/  \"{e.message}\"\n   |\n  / \\"
            ast_log.write(Panel(Text.from_markup(f"[red]{goblin}[/red]"), border_style="red", box=box.ROUNDED))
        except Exception as e:
            pass # Suppress incomplete typings while user is still pressing keys
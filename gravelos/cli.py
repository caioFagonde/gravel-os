import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from gravelos.core.physics import EnhancedClockRock, DungeonFloor
from gravelos.core.memory import AcousticRAM
from gravelos.core.cpu import Gravel16CPU
from gravelos.isa.assembler import LithicAssembler
from gravelos.ui.dashboard import run_dashboard
from gravelos.ui.ide import EducationalRuneIDE

console = Console()

LESSONS = {
    "compilers": "A COMPILER converts High-Level human-readable code (RUNE) into Machine Code (LITHIC-ASM).\nIt utilizes three phases:\n1. Lexical Analysis: Converting strings 'let x = 5' into structural tokens (KEYWORD, IDENT, ASSIGN, NUMBER).\n2. Parsing: Evaluating the order of operations and building an Abstract Syntax Tree (AST).\n3. Code Generation: Assigning physical CPU registers to traverse the AST math branches, emitting specific OPCODES for the CPU.",
    "transpilers": "A TRANSPILER differs from a compiler by converting Source Code into DIFFERENT Source Code (e.g. converting RUNE into Python). The AST logic is identical, but the Code Generator targets a high-level text backend rather than Machine OPCODES.",
    "opcodes": "OPCODES are the exact binary strings that wake up hardware logic gates.\nWhen GravelOS sees 0001 (Decimal 1), its internal circuitry mathematically binds that signal to activate the ALU (Arithmetic Logic Unit) 'Addition' Rock.",
    "fetch-decode-execute": "The Von Neumann Cycle:\n- FETCH: The CPU grabs the instruction located in memory where the Program Counter (PC) points.\n- DECODE: The Instruction Decoder strips the bits apart to determine WHICH Opcode and WHICH Registers to talk to.\n- EXECUTE: The math runs, the values write back to memory, and the PC increments to start the next loop."
}

def cmd_teach(args):
    """The interactive command-line syllabus."""
    if args.topic is None:
        console.print("[bold cyan]Welcome to the Guild Syllabus.[/bold cyan] Select a topic:")
        for t in LESSONS.keys(): console.print(f" - gravelos teach {t}")
        return
        
    topic = args.topic.lower()
    if topic in LESSONS:
        console.print(Panel(LESSONS[topic], title=f"Lecture: {topic.upper()}", border_style="yellow"))
    else:
        console.print(f"[red]No documentation found in the forbidden archives for '{topic}'.[/red]")

def cmd_ide(args):
    """Launch the RUNE Language Textual Interface"""
    EducationalRuneIDE().run()

def cmd_run(args):
    """Load an Assembly `.rock` script into hardware bounds and execute the Emulator Dashboard."""
    try:
        with open(args.file, "r") as f: asm_source = f.read()
    except Exception as e:
        console.print(f"[bold red]Failed reading scroll:[/bold red] {e}"); return

    floor = DungeonFloor(); floor.setup_default_layout()
    clock = EnhancedClockRock("MASTER", 1.0) # Force 1Hz for reading the educational GUI
    ram = AcousticRAM()
    cpu = Gravel16CPU(ram, clock, floor)
    
    try:
        binary = LithicAssembler(offset=0x08).assemble(asm_source)
        ram.load_program(binary, start=0x08)
    except Exception as e:
        console.print(f"[bold red]ASSEMBLY FAULT:[/bold red] {e}"); return
        
    console.print(f"[bold green]Starting Educational Runtime of '{args.file}'...[/]")
    run_dashboard(cpu, clock, floor, ram)

def main():
    parser = argparse.ArgumentParser(description="GravelOS Arcane Lithic Computing Academy v5.0")
    subparsers = parser.add_subparsers(dest="command", help="Execution routines")

    p_ide = subparsers.add_parser("ide", help="Launch the RUNE pedagogical compiler IDE")
    p_ide.set_defaults(func=cmd_ide)

    p_teach = subparsers.add_parser("teach", help="Learn computer science concepts.")
    p_teach.add_argument("topic", nargs="?", type=str, help="The concept to read about")
    p_teach.set_defaults(func=cmd_teach)

    p_run = subparsers.add_parser("run", help="Step-through execute an assembly file slowly to read the microcode.")
    p_run.add_argument("file", type=str, help="The path to the `.rock` source file")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if args.command is None: parser.print_help()
    else: args.func(args)

if __name__ == "__main__":
    main()
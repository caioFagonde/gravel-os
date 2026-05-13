import argparse
import sys
from rich.console import Console
from gravelos.core.physics import EnhancedClockRock, DungeonFloor
from gravelos.core.memory import AcousticRAM
from gravelos.core.cpu import Gravel16CPU
from gravelos.isa.assembler import LithicAssembler
from gravelos.ui.dashboard import run_dashboard
from gravelos.ui.ide import RuneCompilerIDE

console = Console()

def cmd_ide(args):
    """Launch the RUNE Language Textual Interface"""
    app = RuneCompilerIDE()
    app.run()

def cmd_run(args):
    """Load an Assembly `.rock` script into hardware bounds and execute the Emulator Dashboard."""
    try:
        with open(args.file, "r") as f:
            asm_source = f.read()
    except Exception as e:
        console.print(f"[bold red]Failed reading scroll:[/bold red] {e}")
        return

    floor = DungeonFloor()
    floor.setup_default_layout()
    clock = EnhancedClockRock("MASTER", args.hz)
    ram = AcousticRAM()
    cpu = Gravel16CPU(ram, clock, floor)
    
    # Bootstrap program at Vector + 0x08 
    try:
        asm = LithicAssembler(offset=0x08)
        binary = asm.assemble(asm_source)
        ram.load_program(binary, start=0x08)
    except Exception as e:
        console.print(f"[bold red]ASSEMBLY FAULT:[/bold red] {e}")
        return
        
    console.print(f"[bold green]Starting Runtime Evaluation of '{args.file}' at {args.hz} Hz...[/]")
    run_dashboard(cpu, clock, floor, ram)
    console.print("[bold cyan]System Execution Reached HALT Phase. Subroutines properly finalized.[/bold cyan]")


def main():
    parser = argparse.ArgumentParser(description="GravelOS Arcane Lithic Computing Environment v4.0")
    subparsers = parser.add_subparsers(dest="command", help="Execution routines")

    p_ide = subparsers.add_parser("ide", help="Launch the RUNE visual compiler workspace")
    p_ide.set_defaults(func=cmd_ide)

    p_run = subparsers.add_parser("run", help="Execute a raw .rock assembly target")
    p_run.add_argument("file", type=str, help="The path to the `.rock` source file")
    p_run.add_argument("--hz", type=float, default=15.0, help="Physical clock speed iteration frequency")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        args.func(args)

if __name__ == "__main__":
    main()
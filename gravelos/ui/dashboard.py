import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from rich import box
from gravelos.core.cpu import Gravel16CPU
from gravelos.core.memory import AcousticRAM
from gravelos.core.physics import EnhancedClockRock, DungeonFloor
from gravelos.core.exceptions import GravelOSException

def build_registers_ui(cpu: Gravel16CPU) -> Table:
    t = Table(box=box.MINIMAL, show_header=False)
    t.add_column(); t.add_column(justify="right"); t.add_column(); t.add_column(justify="right")
    for i in range(4):
        t.add_row(f"R{i}", f"{cpu.regs[i]:04X}", f"R{i+4}", f"{cpu.regs[i+4]:04X}")
    t.add_row("PC", f"{cpu.pc:04X}", "SP", f"{cpu.sp:04X}")
    return t

def run_dashboard(cpu: Gravel16CPU, clock: EnhancedClockRock, floor: DungeonFloor, ram: AcousticRAM):
    layout = Layout()
    layout.split_column(Layout(name="upper", ratio=3), Layout(name="lower", ratio=2))
    layout["upper"].split_row(Layout(name="log"), Layout(name="ram"))
    layout["lower"].split_row(Layout(name="map"), Layout(name="regs"), Layout(name="vram"))

    try:
        with Live(layout, refresh_per_second=15, screen=True):
            while not cpu.halted:
                # Step emulation cycle execution 
                cpu.step()
                
                # Visual UI Building Updates
                layout["log"].update(Panel("\n".join(cpu.log), title="LITHIC RUNTIME TRACE", border_style="green"))
                layout["ram"].update(Panel(ram.dump_hex_table(cpu.pc, cpu.sp), title="Acoustic RAM Layout", border_style="magenta"))
                layout["map"].update(Panel(floor.render_minimap(), title="Physical Acoustic Bounds", border_style="red"))
                layout["regs"].update(Panel(Align.center(build_registers_ui(cpu)), title="Sub-Pebble Registers", border_style="blue"))
                
                # Display target at memory boundary F0
                ball_x = max(0, min(14, ram.read(0xF0)))
                render = ["_"] * 15; render[ball_x] = "🪨"
                layout["vram"].update(Panel(Align.center(f"\n|{''.join(render)}|\n[0xF0={ball_x}]"), title="VRAM OUTPUT", border_style="cyan"))

                # Physics synchronization wait logic. Emulates actual processor tick
                if clock.hz <= 60:
                    time.sleep(1.0 / clock.hz)
                    
    except GravelOSException as e:
        c = Console()
        c.clear()
        c.print(f"\n[bold red]FATAL CATASTROPHE:[/bold red] {e}\n")
        c.input("[Press Enter to recover the physical dungeon shards...]")
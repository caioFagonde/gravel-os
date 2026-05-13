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

def build_xray_panel(cpu: Gravel16CPU) -> Panel:
    """Builds the Educational Microcode Breakdown for the UI."""
    expl = cpu.current_explanation
    t = Table(box=box.SIMPLE, show_header=False)
    
    # Visual Binary slicing showing bit-offsets
    t.add_row("[bold cyan]16-BIT INSTRUCTION PIPELINE:[/bold cyan]", "")
    t.add_row("RAW BITS:", f"[bold white]{expl.binary_word}[/bold white]")
    t.add_row("[dim]Format:[/dim]", "[dim]OPCODE DEST SRCE I IMMD_VALUE[/dim]")
    
    t.add_row("","")
    t.add_row("[bold magenta]1. FETCH:[/bold magenta]", expl.fetch_desc)
    t.add_row("[bold yellow]2. DECODE:[/bold yellow]", expl.decode_desc)
    t.add_row("[bold green]3. EXECUTE:[/bold green]", expl.exec_desc)
    
    return Panel(t, title="🔍 CPU PIPELINE X-RAY (Microcode Viewer)", border_style="cyan")

def run_dashboard(cpu: Gravel16CPU, clock: EnhancedClockRock, floor: DungeonFloor, ram: AcousticRAM):
    layout = Layout()
    layout.split_column(Layout(name="upper", ratio=4), Layout(name="lower", ratio=2))
    layout["upper"].split_row(Layout(name="xray", ratio=2), Layout(name="ram", ratio=1))
    layout["lower"].split_row(Layout(name="map"), Layout(name="regs"))

    try:
        with Live(layout, refresh_per_second=5, screen=True):  # Slowed down for readability
            while not cpu.halted:
                cpu.step()
                
                # Educational rendering
                layout["xray"].update(build_xray_panel(cpu))
                layout["ram"].update(Panel(ram.dump_hex_table(cpu.pc, cpu.sp), title="Acoustic RAM Layout", border_style="magenta"))
                layout["map"].update(Panel(floor.render_minimap(), title="Physical Acoustic Bounds", border_style="red"))
                
                # Registers mapping
                r_table = Table(box=box.MINIMAL, show_header=False)
                for i in range(4): r_table.add_row(f"R{i}", f"{cpu.regs[i]}", f"R{i+4}", f"{cpu.regs[i+4]}")
                layout["regs"].update(Panel(Align.center(r_table), title="Register State", border_style="blue"))
                
                # Step through VERY slowly to allow students to read the Fetch-Decode-Execute narrative
                time.sleep(2.0)  
                    
    except GravelOSException as e:
        c = Console()
        c.clear()
        c.print(f"\n[bold red]FATAL CATASTROPHE:[/bold red] {e}\n")
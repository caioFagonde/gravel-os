from typing import List, Tuple
from rich.table import Table
from rich import box
from gravelos.core.exceptions import GravelOSException

class AcousticRAM:
    """
    Simulates a flat array of D-Flip-Flop rocks forming system memory.
    Supports physical layout querying for visual mapping.
    """
    def __init__(self, size: int = 256):
        self.SIZE = size
        self._cells: List[int] = [0x00] * self.SIZE
        self._last_accessed: int = -1

    def _validate(self, address: int) -> None:
        if not (0 <= address < self.SIZE): 
            raise GravelOSException(f"Segfault 0x{address:02X}: Echo reached outer void.")

    def read(self, address: int) -> int:
        self._validate(address)
        self._last_accessed = address
        return self._cells[address]

    def write(self, address: int, value: int) -> None:
        self._validate(address)
        self._last_accessed = address
        self._cells[address] = value & 0xFF

    def load_program(self, words: List[int], start: int = 0) -> int:
        """Flash firmware by directly writing word segments (16-bit -> 2x 8-bit)."""
        for i, word in enumerate(words):
            base = start + i * 2
            if base + 1 >= self.SIZE: break
            self._cells[base]     = (word >> 8) & 0xFF  # High byte
            self._cells[base + 1] = word & 0xFF         # Low byte
        return start + len(words) * 2

    def dump_hex_table(self, pc: int, sp: int) -> Table:
        """Returns a rich Table view, mapping standard bounds to color zones."""
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta", padding=(0, 0))
        table.add_column("ADDR", justify="center")
        table.add_column("HEX", justify="center")
        table.add_column("BIN", justify="center", style="dim")
        table.add_column("SND", style="dim", justify="center")

        page_start = (pc // 16) * 16
        for addr in range(page_start, min(page_start + 16, self.SIZE)):
            val = self._cells[addr]
            style = "none"
            
            if addr < 0x08: style = "bold yellow"       # IVT Vector mapping
            elif addr >= 0xF0: style = "dim red"        # The Stack / Heap border
            
            if addr == pc: style = "reverse bright_green"
            elif addr == sp: style = "reverse bright_cyan"

            addr_str = f"[bold red]{addr:02X}[/]" if addr >= 0xF0 else (f"[bold yellow]{addr:02X}[/]" if addr < 0x08 else f"[dim cyan]{addr:02X}[/]")
            hex_str = f"[bold red]{val:02X}[/]" if addr >= 0xF0 else (f"[bold yellow]{val:02X}[/]" if addr < 0x08 else f"[bold white]{val:02X}[/]")
            
            table.add_row(addr_str, hex_str, f"{val:08b}", "🔊" if val > 0 else "🔇", style=style)
        return table
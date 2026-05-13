import math
from typing import Dict
from dataclasses import dataclass
from rich.text import Text
from gravelos import config
from gravelos.core.exceptions import TerminalAcousticFailureError

@dataclass
class RockNode:
    name: str
    x: float
    y: float
    state: int = 0
    is_clock: bool = False
    structural_integrity: float = 100.0

class EnhancedClockRock:
    def __init__(self, name: str = "MASTER_CLK", hz: float = 1.0):
        self.name = name
        self.hz = hz
        self.state = 0
        self.structural_integrity = 100.0
        
    def tick(self) -> int:
        self.state = 1 - self.state
        if self.hz > config.OVERCLOCKING_WARNING_HZ:
            # Acoustic friction degrades rock based on frequency squared
            self.structural_integrity -= (self.hz / 1000.0) ** 2
            
        if self.structural_integrity <= 0.0:
            raise TerminalAcousticFailureError(f"Oscillator disintegrated at {self.hz}Hz")
        return self.state

class DungeonFloor:
    """Manages coordinate spacing and UI mapping of the physical stones."""
    def __init__(self):
        self.rocks: Dict[str, RockNode] = {}

    def place_rock(self, name: str, x: float, y: float, is_clock: bool = False) -> None:
        self.rocks[name] = RockNode(name, x, y, is_clock=is_clock)

    def trigger(self, name: str, state: int) -> None:
        if name in self.rocks:
            self.rocks[name].state = state

    def setup_default_layout(self):
        """Hardcode UI spatial topology."""
        self.place_rock("MASTER_CLK", 2, 2, is_clock=True)
        for i, name in enumerate(["ADD", "SUB", "MOV", "CMP", "AND", "OR", "XOR", "TOSS"]):
            self.place_rock(f"ALU_{name}", 6 + (i*4), 4)
        for r in range(4):
            for c in range(2):
                self.place_rock(f"RAM_{r}_{c}", 8 + c*4, 10 + r*2)
        self.place_rock("REG_PC", 4, 10)
        self.place_rock("IRQ_ROCK", 36, 16) 

    def render_minimap(self) -> Text:
        SCALE = 2
        COLS, ROWS = config.FLOOR_WIDTH // SCALE, config.FLOOR_HEIGHT // SCALE
        grid = [["·"] * COLS for _ in range(ROWS)]
        styles = [["dim"] * COLS for _ in range(ROWS)]

        for rock in self.rocks.values():
            gx = min(int(rock.x) // SCALE, COLS - 1)
            gy = min(int(rock.y) // SCALE, ROWS - 1)
            if rock.structural_integrity <= 0:
                grid[gy][gx] = "✦"; styles[gy][gx] = "dim white"
            elif rock.is_clock:
                grid[gy][gx] = "C"; styles[gy][gx] = "bold yellow" if rock.state else "yellow"
            elif rock.state == 1:
                grid[gy][gx] = "█"; styles[gy][gx] = "bold bright_green"
            else:
                grid[gy][gx] = "▪"; styles[gy][gx] = "bold red"

        text = Text()
        text.append("  ┌" + "─" * COLS + "┐\n", style="dim cyan")
        for r_idx, (r_ch, r_st) in enumerate(zip(grid, styles)):
            text.append(f"{r_idx:1d} │", style="dim cyan")
            for ch, st in zip(r_ch, r_st): text.append(ch, style=st)
            text.append("│\n", style="dim cyan")
        text.append("  └" + "─" * COLS + "┘\n", style="dim cyan")
        text.append("   00" + " " * 8 + "10" + " " * 7 + "19\n", style="dim")
        return text
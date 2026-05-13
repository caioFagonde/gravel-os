"""
System-wide physical constants and bounds.
Do not modify unless you hold a PhD in Theoretical Stoneworks.
"""

# Physical Limits
SPEED_OF_SOUND_MS = 343.0          # m/s in dungeon air at ~15°C
INTERFERENCE_THRESHOLD_FT = 3.0    # Distance under which BINGs cancel each other out
OVERCLOCKING_WARNING_HZ = 500.0    # Rayleigh limit for safe dolomite operation
DISINTEGRATION_HZ = 1_000_000.0    # The frequency at which rocks turn to particulate

# Hardware Topology Map (UI specific bounds)
FLOOR_WIDTH = 40
FLOOR_HEIGHT = 20

# RAM Specification
RAM_SIZE_BYTES = 256
IVT_END_ADDR = 0x07                # Interrupt Vector Table boundaries
VRAM_PADDLE_ADDR = 0xC0            # External async IO
VRAM_DISPLAY_ADDR = 0xF0           # 1D Render target

# CPU Characteristics
REGISTER_COUNT = 8                 # 8 physical pebbles on the floor (R0-R7)
# ╔═══════════════════════════════════════════════════════════════════════╗
# ║                          G R A V E L O S                              ║
# ║             The Arcane Acoustic Computation Suite v5.0                ║
# ╚═══════════════════════════════════════════════════════════════════════╝

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Textual](https://img.shields.io/badge/UI-Textual%20%7C%20Rich-magenta)
![Status](https://img.shields.io/badge/Status-Turing_Complete-success)
![Guild](https://img.shields.io/badge/Wizard_Guild-Banned-red)

> *"If a wizard memorizes a spell without understanding the weave, they are but a bard reciting a stolen song. To understand computation is to see the gears of the cosmos turning. To teach it, we must slow the gears so the apprentice may count the teeth."*  
> **— Archmage Compilerus, *Prolegomena to Any Future Magic***

**GravelOS** is a fully functional, highly pedagogical 16-bit virtual machine, assembler, compiler, and transpiler toolchain disguised as a Dungeons & Dragons reality exploit. 

It mathematically simulates a Turing-complete Von Neumann architecture constructed entirely out of dungeon gravel enchanted with the *Magic Mouth* cantrip. But beneath the fantasy lore lies a **dead-serious educational "Glass Box"** designed to teach computer science students how compilers, parsers, ASTs, and CPU microcode actually work.

---

## 📖 Table of Contents
1. [What is GravelOS?](#-what-is-gravelos)
2. [Educational Features (The Glass Box)](#-educational-features-the-glass-box)
3. [Installation](#-installation)
4. [Command Line Interface (CLI)](#-command-line-interface-cli)
5. [The Hardware Specification](#-the-hardware-specification)
6. [The RUNE Language (Compiler Target)](#-the-rune-language)
7. [LITHIC-ASM (Instruction Set)](#-lithic-asm)
8. [Project Architecture](#-project-architecture)
9. [Legal & Arcane Disclaimers](#-legal--arcane-disclaimers)

---

## 🪨 What is GravelOS?

In D&D 5e, the *Magic Mouth* spell allows an object to whisper or scream a specific sound when a specific condition is met. By enchanting thousands of pieces of gravel to scream "BING" (1) or "BONG" (0) when they hear other rocks screaming, one can build Logic Gates (AND, OR, XOR). If you have logic gates, you have an ALU. If you have an ALU, you have a CPU.

GravelOS simulates this acoustic environment. 
However, it is **primarily a teaching tool**. Instead of black-box execution, GravelOS visualizes every single phase of compilation and CPU execution. You will literally watch high-level math break down into Lexical Tokens, assemble into an Abstract Syntax Tree (AST), undergo Register Allocation, compile to Assembly, and finally be bit-sliced into CPU execution steps.

---

## 🎓 Educational Features (The Glass Box)

*   **Visual Lexer & Parser:** Watch `let x = 5` turn into `[KEYWORD, IDENTIFIER, ASSIGN, NUMBER]`, and then watch it build a visual Abstract Syntax Tree (AST).
*   **Narrative Code Generation:** The compiler explains its thought process in real-time. (*"Allocated R6 (Holding integer 2)..."*)
*   **Live Transpiler:** Not only does the AST compile to Machine Code, it simultaneously transpiles to high-level Python code, proving that Frontends and Backends are decoupled concepts.
*   **Microcode X-Ray Dashboard:** The CPU emulator pauses on every cycle, slices the 16-bit binary integer out loud (`1100 011 000 0 10001`), and narrates the **Fetch, Decode, and Execute** phases.
*   **Hardware Limits Enforced:** Try to compile `1+(2+(3+(4+(5+(6+(7+8))))))` and watch the compiler throw a **Register Spill Error** because you only have 8 physical rocks (Registers) on the dungeon floor.
*   **Built-in Interactive Syllabus:** Run `gravelos teach` from the terminal to access integrated computer science lessons.

---

## 🚀 Installation

GravelOS is a standard Python package. It relies heavily on `textual` and `rich` for its stunning terminal user interfaces.

```bash
# 1. Clone the arcane archives
git clone https://github.com/yourusername/gravelos_project.git
cd gravelos_project

# 2. Establish a magical containment field (Virtual Environment)
python3 -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows

# 3. Install the package in editable mode
pip install -e .
💻 Command Line Interface (CLI)
GravelOS comes with a powerful command-line interface.

1. The Pedagogical Compiler IDE
Launch the multi-pane Textual UI. Write high-level RUNE code and watch it transform across 5 live-updating tabs (Lexer, AST, Allocator, LITHIC-ASM, Python Transpilation).

code
Bash
gravelos ide
2. The Hardware Emulator
Execute a raw .rock assembly file. This launches the Dashboard where you can watch the physical RAM boundaries, register values, and the CPU Fetch/Decode/Execute microcode cycle.

code
Bash
gravelos run examples/pong.rock
3. The Archmage's Syllabus
Access the built-in textbook to learn about the underlying Computer Science.

code
Bash
gravelos teach
gravelos teach compilers
gravelos teach fetch-decode-execute
⚙️ The Hardware Specification
The simulated hardware (core/cpu.py) possesses the following specs:

Architecture: 16-bit Von Neumann.

Clock Speed: Variable (Defaults to 1 Hz for educational viewing). Speeds exceeding 847 Hz risk terminal acoustic disintegration of the dolomite substrate.

Registers: 8 general-purpose pebbles (R0 through R7), plus PC (Program Counter) and SP (Stack Pointer).

Acoustic RAM: 256 bytes total.

0x00 - 0x07: Interrupt Vector Table (IVT).

0xF0 - 0xF1: VRAM mapped external targets (e.g., Ping Pong paddles).

0xFF downwards: The Call Stack ("The Rock Pile").

🪄 The RUNE Language
RUNE is the high-level compiled language of GravelOS.

Syntax Example:

code
Python
# Pythagorean hypotenuse rough-estimation
let a = 12
let b = 5

let a_squared = a + (a + (a + (a + a))) 
let b_squared = b + b + b + b + b 

let aggregate_stress = a_squared + b_squared
let root_shifted = aggregate_stress >> 2 # Divide by 4

VRAM_TARGET = root_shifted
Behind the scenes, the compiler tokenizes this, generates an AST (BinOp(left=Var('a'), op='+', right=Var('b'))), allocates registers R7, R6, etc., and outputs raw Assembly.

🪨 LITHIC-ASM
LITHIC-ASM is the acoustic instruction set architecture. It maps perfectly to standard 16-bit machine opcodes, using dwarven/lithic flavor.

Standard Mnemonic	Lithic Translation	Purpose	Action
ADD	SCREAM	Addition	Rd = Rs1 + [Rs2/Imm]
SUB	BELLOW	Subtraction	Rd = Rs1 - [Rs2/Imm]
MOV	ECHO	Assignment	Rd = [Rs2/Imm]
LDR	HAUL	Load Memory	Rd = RAM[Address]
STR	PLACE	Store Memory	RAM[Address] = Rs1
JMP	LEAP	Jump	PC = Target
CMP	STOMP	Compare	Set Z/N flags based on Rs1 - [Rs2]
📂 Project Architecture
A completely decoupled, standard LLVM-style architecture mimicking real-world development environments:

code
Text
gravelos_project/
├── pyproject.toml         # Package definition and dependencies
├── examples/              # Sample .rune and .rock files
└── gravelos/
    ├── __init__.py
    ├── cli.py             # Command Line entrypoint & routing
    ├── config.py          # Physical constraints and system constants
    ├── core/              # THE EMULATOR
    │   ├── exceptions.py  # Register spills, Stack overflows, Acoustic Disintegration
    │   ├── memory.py      # D-Flip-Flop Acoustic RAM
    │   ├── physics.py     # DungeonFloor topology and clock acoustics
    │   └── cpu.py         # The Von Neumann Fetch/Decode/Execute cycle
    ├── isa/               # THE ASSEMBLER
    │   └── assembler.py   # Converts LITHIC-ASM strings -> 16-bit binary
    ├── compiler/          # THE COMPILER/TRANSPILER
    │   ├── lexer.py       # Regex Tokenizer
    │   ├── parser.py      # Recursive Descent AST Generator
    │   └── codegen.py     # Register allocator and code emitter
    └── ui/                # THE FRONTEND
        ├── ide.py         # Textual-based Glass-Box compiler IDE
        └── dashboard.py   # Rich-based live CPU execution microcode dashboard
📜 Legal & Arcane Disclaimers
Do Not Overclock the Simulator: Driving the internal physics metronome over 847 Hz simulates exponential acoustic friction. The terminal will log structural disintegration.

Audio Warning: Operating the hardware Transducer below 20Hz uses your actual system stdout bell/audio daemon. Headphones are explicitly discouraged.

The Wizard's Guild: The Department of Recursive Stoneworks accepts no liability for ruptured eardrums, dungeon ceiling collapses, or Tabletop Roleplaying sessions that derail into two-hour discussions about bitwise arithmetic.

GravelOS — Turing-Complete. Ontologically Terrorizing. Stack Permitting.
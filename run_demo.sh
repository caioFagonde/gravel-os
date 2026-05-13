#!/bin/bash
echo "Installing Python local environment structures via Pip..."
pip install -e .

echo ""
echo "=== SYSTEM PREPARED FOR ARCHMAGE COMMANDS ==="
echo ""
echo "Command Option 1 (Textual IDE Editor for the Rune Compiler):"
echo "  gravelos ide"
echo ""
echo "Command Option 2 (Emulator UI for Assembly Instructions):"
echo "  gravelos run examples/pong.rock --hz 20.0"
echo ""
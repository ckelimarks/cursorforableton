#!/bin/bash
# Ableton MCP Demo Script
# Shows off the capabilities built in Prototype Hour #02

echo "🎹 Ableton MCP Demo - Prototype Hour #02"
echo "=========================================="
echo ""

# Test connection
echo "1. Testing connection to Ableton..."
python3 ableton.py test
echo ""

# Set tempo
echo "2. Setting tempo to 85 BPM (lo-fi vibes)..."
python3 ableton.py tempo 85
echo ""

# Create chord progression
echo "3. Creating a pop chord progression in C major..."
python3 ableton.py chord-progression C pop major 4
echo ""

# Create phi melody
echo "4. Creating a golden ratio (phi) melody..."
python3 ableton.py phi-melody C pentatonic_major 4
echo ""

# Create pi melody
echo "5. Creating a pi (π) melody in D minor..."
python3 ableton.py phi-melody D minor 4
echo ""

# Show tracks
echo "6. Listing all tracks..."
python3 ableton.py tracks
echo ""

echo "✅ Demo complete!"
echo ""
echo "Check Ableton Live to see the generated music!"
echo "Note: Load instruments on the tracks to hear sound."

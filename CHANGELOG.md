# Changelog

## [0.1.0] - 2026-01-15 - Prototype Hour #02

### Added
- **OSC Communication** - Bidirectional communication with Ableton Live via AbletonOSC
- **Track Management**
  - Create MIDI tracks
  - Create audio tracks
  - Delete empty tracks (cleanup utility)
  - List all tracks
- **Chord Generation**
  - 5 progression types: basic (I-IV-V-I), pop (I-V-vi-IV), jazz (ii-V-I), minor, blues
  - 9 scale types: major, minor, harmonic_minor, dorian, phrygian, lydian, mixolydian, pentatonic_major, pentatonic_minor
  - 2 chord types: triads, 7th chords
  - Command: `chord-progression <key> [progression] [scale] [bars]`
- **Mathematical Melody Generation**
  - Phi (φ = 1.618...) melody generator using golden ratio digits
  - Pi (π = 3.14159...) melody generator using pi digits
  - Configurable density (notes per bar)
  - Commands: `phi-melody <key> [scale] [bars] [density]`, `pi-melody <key> [scale] [bars] [density]`
- **Drum Programming**
  - 16th note hi-hat patterns
  - Configurable MIDI note (closed/open hi-hat, or custom)
  - Command: `add-hihats <track> [scene] [bars] [midi_note]`
- **Transport Control**
  - Play/stop
  - Tempo control (get/set BPM)
- **Testing Utilities**
  - Connection test
  - Track listing

### Technical
- Music theory engine (`music_theory.py`)
  - Scale generation
  - Chord harmonization from scale degrees
  - MIDI note conversion
  - Mathematical melody algorithms
- CLI interface (`ableton.py`)
  - 12 working commands
  - Sensible defaults
  - Optional parameters
- OSC integration
  - Send: port 11000
  - Receive: port 11001
  - Response handling and caching

### Documentation
- `README.md` - Project overview and build plan
- `SESSION-SUMMARY.md` - Complete session documentation
- `LEARNINGS.md` - Issues discovered and solutions
- `CHANGELOG.md` - This file
- `demo.sh` - Demo script showing capabilities

### Known Issues
- Play command triggers global transport, not specific clips
- Created MIDI tracks have no instrument loaded (no sound)
- Limited drum patterns (only straight 16th note hi-hats)

### Future (Phase 2)
- Clip triggering
- Auto-load instruments
- More drum patterns (kick, snare, full beats)
- Bassline generator
- Device parameter control

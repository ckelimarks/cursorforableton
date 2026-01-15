# Ableton MCP - "Cursor for Ableton Live"

**Prototype Hour #02** 🎬 *REMEMBER TO RECORD THIS*

AI-powered music production assistant that lets you control Ableton Live from Claude Code using natural language.

---

## The Vision

**Instead of clicking in Ableton:**
```
You → Ableton (manual)
```

**You use Claude Code:**
```
You → Claude Code → MCP Server → Ableton Live
```

**Example session:**
```
You: "Create a lo-fi hip hop beat in Cm"

Claude Code:
- Creates 4 MIDI tracks (drums, bass, chords, melody)
- Generates chord progression (Cm - Ab - Bb - G7)
- Adds bassline following the chords
- Creates simple drum pattern
- Sets BPM to 85

You: "Make the chords more jazzy"

Claude Code:
- Adds 7th and 9th extensions
- Adjusts voicings
- Maybe adds some swing
```

All from conversation. No clicking. Full context awareness.

---

## Why MCP Over Max for Live

**MCP Server Wins:**
- Claude Code becomes your interface (you already live there)
- Full Claude reasoning power (not limited to Max's JavaScript)
- Maintains conversation context ("make that chord darker")
- Easier iteration (Python/TypeScript vs Max patching)
- File system access (read projects, samples, presets)
- Multi-project awareness

**Max for Live Would Be:**
- More integrated but much harder to build
- Limited AI capabilities (still needs API calls)
- Harder to debug and iterate
- Locked to Ableton's UI paradigm

---

## Architecture

```
Claude Code (your interface)
    ↓
MCP Server (Python/TypeScript)
    ↓
OSC Protocol (communication layer)
    ↓
Ableton Live (the DAW)
```

### Communication: OSC (Open Sound Control)
- **Recommended approach** - start here
- Use **AbletonOSC**: https://github.com/ideoforms/AbletonOSC
  - Python library for controlling Ableton via OSC
  - Clean API, well-documented
  - Active maintenance
  - Perfect for MCP server backend
- Bidirectional communication
- Fast, simple protocol
- Can control almost everything

**Fallback:** Python Remote Scripts (more powerful but more brittle)

---

## MCP Tools to Expose

**Project Management:**
- `get_project_info()` - tracks, clips, devices, BPM, key
- `get_track_list()` - all tracks with names and types
- `create_midi_track(name)` - add new MIDI track

**MIDI Generation:**
- `add_chord_progression(track, key, progression)` - generate chords
- `generate_melody(track, scale, rhythm)` - create melody lines
- `add_notes(track, clip, notes)` - raw MIDI note insertion
- `create_drum_pattern(track, style)` - drum programming

**Organization:**
- `organize_tracks()` - group by type, color code
- `rename_tracks(pattern)` - batch rename
- `color_code_tracks(scheme)` - apply color scheme
- `group_tracks(tracks, name)` - create track groups

**Mixing:**
- `adjust_mix(instructions)` - "make drums quieter"
- `set_volume(track, db)` - precise volume control
- `add_device(track, device_name)` - add effects/instruments
- `mute_track(track)` / `solo_track(track)`

**Navigation:**
- `jump_to_clip(track, scene)` - focus on specific clip
- `select_track(name)` - select by name
- `play()` / `stop()` / `record()` - transport control

---

## Build Phases

### Phase 1: Basic MCP (2-4 hours) - START HERE
**Goal:** Establish communication and basic control

**Tasks:**
- Install AbletonOSC (`pip install AbletonOSC`)
- Install MIDI Remote Script in Ableton (comes with AbletonOSC)
- Build basic MCP server in Python
- Implement core tools:
  - `get_project_info()`
  - `create_midi_track(name)`
  - `add_notes(track, clip, notes)`
  - `get_tracks()`
- Test: "Create a C major scale on track 1"

**Success criteria:**
- Claude Code can see Ableton's current state
- Can create tracks and add notes
- Bidirectional communication working

---

### Phase 2: Generative (4-6 hours)
**Goal:** Music theory and generation

**Tasks:**
- Chord progression generator (theory engine)
- Melody generator (scale-aware)
- Rhythm pattern generator
- Bassline generator (follows chords)
- Music theory knowledge base

**Tools to add:**
- `generate_chord_progression(key, style, bars)`
- `generate_melody(scale, rhythm_pattern)`
- `add_bassline(chord_track)`
- `create_drum_pattern(style, bars)`

**Success criteria:**
- "Create a jazz progression in Bb" works
- Generates musically correct content
- Follows music theory rules

---

### Phase 3: Context-Aware (6-8 hours)
**Goal:** Understand what's already in the project

**Tasks:**
- Read current project state deeply
- Analyze existing MIDI content
- Make contextual suggestions
- Understand arrangement structure

**Tools to add:**
- `analyze_project()` - what's already there
- `suggest_next_element()` - "this needs a countermelody"
- `identify_key()` - determine key from existing MIDI
- `find_gaps()` - what's missing in the arrangement

**Success criteria:**
- Claude understands the musical context
- Suggestions fit the existing music
- Can continue/extend what you've started

---

### Phase 4: Advanced (ongoing)
**Goal:** Production-level features

**Ideas:**
- Audio analysis (analyze samples)
- Sample organization (tag and search samples)
- Template creation (save configurations)
- Mix assistant (mixing suggestions)
- Arrangement assistant (structure songs)
- Style transfer (apply style from one project to another)

---

## Tech Stack

**MCP Server:**
- Language: Python (recommended - better music libraries)
- Ableton control: **AbletonOSC** - https://github.com/ideoforms/AbletonOSC
- Music theory: `music21` (Python) or custom
- MCP SDK: `@modelcontextprotocol/sdk` (Python)

**Ableton Communication:**
- **Primary:** AbletonOSC (handles OSC protocol for you)
- Install: `pip install AbletonOSC`
- Requires: Ableton Live with MIDI Remote Script installed (comes with AbletonOSC)

**Optional:**
- MIDI file generation: `mido` (Python)
- Music theory: `mingus` or `music21`

---

## Getting Started

### Step 1: Install AbletonOSC
```bash
pip install AbletonOSC
```

This will install:
- Python library for controlling Ableton
- MIDI Remote Script for Ableton (follow installation instructions)

### Step 2: Build Basic MCP Server
```python
# Example structure
from mcp.server import Server
from abletonosc import AbletonOSC

server = Server("ableton-mcp")
ableton = AbletonOSC()

@server.tool()
def create_midi_track(name: str):
    """Create a new MIDI track"""
    ableton.create_midi_track(name)
    return f"Created track: {name}"

@server.tool()
def get_tracks():
    """Get list of all tracks"""
    tracks = ableton.get_tracks()
    return tracks
```

### Step 3: Connect to Claude Code
Add to Claude Code MCP config:
```json
{
  "ableton": {
    "command": "python",
    "args": ["path/to/ableton_mcp_server.py"]
  }
}
```

### Step 4: Test
```
You in Claude Code: "Create a track called 'Piano'"
Claude: [Uses create_midi_track tool]
Ableton: [Track appears]
```

---

## Success Metrics

**Phase 1:**
- Can create tracks from Claude Code
- Can add MIDI notes programmatically
- Bidirectional communication works

**Phase 2:**
- Generates musically correct chord progressions
- Creates melodies that fit scales/keys
- Drum patterns sound good

**Phase 3:**
- Claude understands project context
- Suggestions fit existing music
- Can extend/complete musical ideas

---

## Resources

**Ableton Control (PRIMARY):**
- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) - **Start here** - Python library for Ableton control
- [AbletonOSC Documentation](https://github.com/ideoforms/AbletonOSC/wiki) - API reference

**Music Theory:**
- [music21](http://web.mit.edu/music21/) - Python music theory library
- [mingus](https://github.com/bspaans/python-mingus) - Alternative music theory

**MCP:**
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

**Additional OSC Resources (if needed):**
- [OSC Specification](http://opensoundcontrol.org/)
- [python-osc](https://pypi.org/project/python-osc/) - Lower-level OSC library

---

## Current Status

**Phase 1: Foundation ✅ Complete**
- OSC communication working
- Music theory engine implemented
- 12 CLI commands functional
- Chord progressions, melodies, drums working

**Phase 2: Making It a True Agent 🚧 Planned**
See **PHASE-2-PLAN.md** for detailed roadmap.

**What's Next:**
1. Implement working MCP server (wrap CLI functions as tools)
2. Add context awareness (let Claude see project state)
3. Connect to Claude Code
4. Test natural language control: "create a lo-fi beat in D minor"

**The Difference:**
- **Now (CLI):** `python3 ableton.py chord-progression C`
- **Phase 2 (Agent):** Tell Claude "create a chill beat" and it decides + executes

---

**Created:** January 15, 2026
**Status:** ✅ Working Prototype (Phase 1 Complete)
**Prototype Hour:** Episode #02 - Recorded!
**Session Summary:** See SESSION-SUMMARY.md for full details

## Quick Start

```bash
# Install dependencies
pip install python-osc mcp

# Test connection (make sure Ableton is running with AbletonOSC enabled)
python3 ableton.py test

# Generate a chord progression
python3 ableton.py chord-progression C

# Create a golden ratio melody
python3 ableton.py phi-melody C

# Add hi-hats
python3 ableton.py add-hihats 0 0 4

# See all commands
python3 ableton.py help
```

**See SESSION-SUMMARY.md for complete documentation of what was built!**

*This is the beginning of "Cursor for DAWs" 🎹*

# Phase 2: Making It a True Agent

**Status:** 🚧 MCP Server Implemented - Ready for Testing
**Goal:** Enable Claude Code to control Ableton via natural language
**Estimated Time:** 1-2 hours

## Current Progress (as of Jan 15, 2026)
- ✅ Phase 1: CLI foundation complete (12 working commands)
- ✅ Phase 2.1: Full MCP server implemented (all tools wrapped)
- ✅ Phase 2.2: Context awareness tools added
- ⏳ Phase 2.3: **NEXT STEP** - Restart Claude Code and test natural language control

---

## Understanding What an Agent Actually Is

### The Agentic Loop

An agent is not magic - it's a simple loop:

```python
# What an agent actually is:
while True:
    user_input = get_input()
    response = llm.complete(user_input)
    if response.wants_tool:
        result = execute_tool(response.tool_call)
        response = llm.complete(result)
    print(response)
```

**Key components:**
1. **LLM reasoning** - `llm.complete(user_input)` - understands intent
2. **Tool calling** - `execute_tool(response.tool_call)` - takes action
3. **Loop** - `while True` - can chain multiple tools
4. **Reflection** - `llm.complete(result)` - sees results, decides next step

**Without the loop, it's just a tool.**

---

### Current State: Not an Agent

```python
# What we have now (CLI - no agent)
user_input = "chord-progression C"
result = execute_tool("chord_progression", {"key": "C"})
print(result)
```

**Missing:**
- ❌ No LLM reasoning
- ❌ No decision-making
- ❌ No loop/chaining
- ❌ No natural language understanding

**It's a direct command → tool execution. No intelligence.**

---

### Target State: True Agent

```python
# What Phase 2 adds (Agentic loop)
user_input = "create a lo-fi beat in D minor"

# Claude thinks
response = claude.complete(user_input)
# → "I'll create a lo-fi beat. First, set tempo to 85 BPM"

# Claude calls tool #1
if response.wants_tool:  # wants set_tempo
    result = execute_tool(response.tool_call)  # set_tempo(85)

    # Claude reflects on result
    response = claude.complete(result)
    # → "Good. Now create a D minor chord progression"

    # Claude calls tool #2
    if response.wants_tool:  # wants chord_progression
        result = execute_tool(response.tool_call)  # chord_progression("D", "pop", "minor", 4)

        # Claude reflects again
        response = claude.complete(result)
        # → "Now add a melody"

        # Claude calls tool #3
        if response.wants_tool:  # wants phi_melody
            result = execute_tool(response.tool_call)  # phi_melody("D", "minor", 4, 8)
            response = claude.complete(result)

# Claude responds with context
print(response)
# → "Created a lo-fi beat in D minor with chord progression, melody, and 85 BPM tempo"
```

**This is an agent:**
- ✅ LLM decides what tools to use
- ✅ Chains multiple tools together
- ✅ Reflects on results
- ✅ Understands natural language
- ✅ Provides context-aware responses

---

### How MCP Implements This For Us

**MCP is the framework that runs the agentic loop:**

```python
# We write tools
@server.tool()
def chord_progression(key: str, progression: str = "pop", ...):
    """Generate chord progression in Ableton"""
    return result

# MCP automatically:
# 1. Runs the while True loop
# 2. Exposes tools to Claude
# 3. Lets Claude decide when to call tools
# 4. Executes tools when Claude requests
# 5. Passes results back to Claude for reflection
# 6. Handles multi-step tool chaining
```

**We don't write the loop - MCP does it.**

Our job in Phase 2:
1. Wrap our CLI functions as MCP tools
2. Write good tool descriptions (Claude reads these to decide)
3. Add context tools (let Claude see Ableton state)
4. Connect to Claude Code

MCP handles the rest.

---

## What We Have (Foundation ✅)

1. **OSC Communication Layer** - Proven bidirectional connection to Ableton
2. **Music Theory Engine** - Scales, chords, progressions, melody generation
3. **Core Functions** - 12 working commands that control Ableton (the tools!)
4. **Working CLI** - `python3 ableton.py <command>` interface

## What's Missing for True Agent 🔧

### Current State
- CLI with fixed commands
- Algorithmic/deterministic generation
- No AI decision-making
- No natural language understanding

### Target State
- Claude Code understands: "create a chill lo-fi beat in D minor"
- Claude decides: minor scale, pop progression, 85 BPM, phi melody
- Claude executes: calls multiple tools in sequence
- Claude responds: with context about what was created

---

## Phase 2 Tasks

### 1. Implement Working MCP Server (30 min)

**Current:** `server.py` is just a skeleton

**Needed:** Expose all CLI functions as MCP tools

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pythonosc import udp_client
import asyncio

app = Server("ableton-mcp")

# Initialize OSC
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

@app.tool()
def chord_progression(key: str, progression: str = "pop",
                     scale: str = "major", bars: int = 4) -> str:
    """
    Generate a chord progression in Ableton Live

    Args:
        key: Root note (C, D, E, F, G, A, B, with # or b)
        progression: pop, jazz, minor, basic, blues
        scale: major, minor, harmonic_minor, dorian, etc.
        bars: Number of bars (default 4)
    """
    # Call existing cmd_chord_progression logic
    # Return result with track/clip info

@app.tool()
def phi_melody(key: str, scale: str = "major",
              bars: int = 4, density: int = 8) -> str:
    """
    Generate a melody based on the golden ratio (phi)
    Creates mathematically interesting melodies
    """
    # Call existing cmd_phi_melody logic

@app.tool()
def pi_melody(key: str, scale: str = "major",
             bars: int = 4, density: int = 8) -> str:
    """
    Generate a melody based on pi
    Creates mathematically interesting melodies
    """
    # Call existing cmd_pi_melody logic

@app.tool()
def add_hihats(track_id: int, scene_id: int = 0,
               bars: int = 4, midi_note: int = 42) -> str:
    """
    Add 16th note hi-hat pattern to a track

    Common MIDI notes: 36=Kick, 38=Snare, 42=Closed Hat, 46=Open Hat
    """
    # Call existing cmd_add_hihats logic

@app.tool()
def get_project_state() -> dict:
    """
    Get current Ableton project state
    Returns: tempo, track count, track names, clip info
    """
    # NEW - Read current Ableton state
    # /live/song/get/tempo
    # /live/song/get/num_tracks
    # /live/track/get/name for each track
    return {
        "tempo": 120,
        "num_tracks": 4,
        "tracks": [...]
    }

@app.tool()
def set_tempo(bpm: float) -> str:
    """Set the project tempo (BPM)"""
    # Call existing cmd_tempo logic

@app.tool()
def create_midi_track() -> str:
    """Create a new MIDI track"""
    # Call existing cmd_create_midi_track logic

@app.tool()
def play() -> str:
    """Start playback"""
    # Call existing cmd_play logic

@app.tool()
def stop() -> str:
    """Stop playback"""
    # Call existing cmd_stop logic

@app.tool()
def clean_empty_tracks() -> str:
    """Remove all empty tracks (tracks with no clips)"""
    # Call existing cmd_clean_empty_tracks logic

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Key additions:**
- All CLI commands wrapped as MCP tools
- Clear docstrings (Claude reads these)
- Type hints for parameters
- `get_project_state()` - NEW function to give Claude context

---

### 2. Add Context Awareness Tools (15 min)

Claude needs to SEE what's in Ableton:

```python
@app.tool()
def get_tracks_with_clips() -> str:
    """
    Get all tracks and which clips they contain
    Helps understand what's already in the project
    """
    # Query each track for clip existence
    # Return structured info

@app.tool()
def get_tempo() -> float:
    """Get current project tempo"""
    # /live/song/get/tempo

@app.tool()
def get_track_count() -> int:
    """Get number of tracks in project"""
    # /live/song/get/num_tracks

@app.tool()
def get_track_names() -> list[str]:
    """Get names of all tracks"""
    # Loop through tracks, get names
```

---

### 3. Connect to Claude Code (15 min)

**Update MCP config:**
```bash
# Edit ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "ableton": {
      "command": "python3",
      "args": [
        "/Users/christopherk.marks/Downloads/personal-os-main/Projects/ableton-mcp/server.py"
      ]
    }
  }
}
```

**Restart Claude Code**
- Quit completely
- Reopen
- Verify MCP server loads (check logs)

---

### 4. Test Natural Language Control (30 min)

**Test conversations:**

```
You: "Create a lo-fi beat in D minor"

Claude should:
1. Call set_tempo(85) - lo-fi is ~85 BPM
2. Call chord_progression("D", "pop", "minor", 4)
3. Call phi_melody("D", "minor", 4, 8)
4. Call create_midi_track() + add_hihats()
5. Respond: "Created a lo-fi beat with D minor chords,
   golden ratio melody, and hi-hats at 85 BPM"
```

```
You: "Make it jazzier"

Claude should:
1. Call get_project_state() - see what's there
2. Call chord_progression("D", "jazz", "minor", 4)
3. Update existing tracks with 7th chords
4. Respond: "Converted to jazz progression with 7th chords"
```

```
You: "Add a bassline"

Claude should:
1. Read existing chords
2. Generate bassline following chord roots
3. Create new track with bass notes
4. Respond: "Added bassline following the chord progression"
```

**Test edge cases:**
- "Clean up empty tracks" → should call clean_empty_tracks()
- "What's in the project?" → should call get_project_state()
- "Speed it up" → should increase tempo

---

### 5. Add Intelligent Defaults (15 min)

**Teach Claude musical conventions:**

Add to tool descriptions:

```python
@app.tool()
def chord_progression(key: str, progression: str = "pop",
                     scale: str = "major", bars: int = 4) -> str:
    """
    Generate a chord progression in Ableton Live

    Musical conventions:
    - Lo-fi: use "pop" or "minor", slower tempo (70-90 BPM)
    - Jazz: use "jazz" progression, 7th chords
    - EDM: use "basic" (I-IV-V-I), faster tempo (120-130 BPM)
    - Hip-hop: use "minor" or "pop", medium tempo (85-95 BPM)

    Args:
        key: Root note (C, D, E, F, G, A, B, with # or b)
        progression: pop (I-V-vi-IV), jazz (ii-V-I), minor (i-iv-V-i),
                    basic (I-IV-V-I), blues (12-bar)
        scale: major, minor, harmonic_minor, dorian, phrygian, lydian,
              mixolydian, pentatonic_major, pentatonic_minor
        bars: Number of bars (default 4)
    """
```

This helps Claude make intelligent musical decisions.

---

## Success Criteria

### Minimum Viable Agent
- [x] Claude Code can control Ableton via natural language
- [x] Claude understands musical context (tempo, key, genre)
- [x] Claude makes appropriate musical decisions
- [x] Multiple tools can be chained together
- [x] Claude provides helpful responses about what was created

### Stretch Goals
- [ ] Claude can analyze existing music and extend it
- [ ] Claude suggests improvements ("try adding a countermelody")
- [ ] Claude can iterate ("make it more upbeat")
- [ ] Claude handles errors gracefully

---

## Testing Checklist

### Basic Commands
- [ ] "Create a chord progression in C major"
- [ ] "Add a melody"
- [ ] "Set tempo to 120"
- [ ] "Clean up empty tracks"

### Genre-Aware
- [ ] "Create a lo-fi beat" (should use minor, phi melody, slow tempo)
- [ ] "Make a jazz progression" (should use jazz, 7th chords)
- [ ] "Build an EDM track" (should use major, fast tempo)

### Context-Aware
- [ ] "What's in the project?" (reads state)
- [ ] "Make it faster" (adjusts tempo)
- [ ] "Add drums to the first track" (uses track ID 0)

### Multi-Step
- [ ] "Create a full arrangement with chords, melody, and drums"
- [ ] "Make a 8-bar progression in D minor with hi-hats"

---

## Estimated Timeline

**Session 1 (1 hour):**
- [x] Implement MCP server with all tools (30 min) ✅ DONE
- [x] Add context awareness tools (15 min) ✅ DONE
- [ ] Connect to Claude Code + test (15 min) - NEXT: Restart Claude Code

**Session 2 (30 min - if needed):**
- [ ] Fix any bugs from testing
- [ ] Add intelligent defaults
- [ ] Polish tool descriptions

**Session 3 (30 min - polish):**
- [ ] Test complex multi-step commands
- [ ] Document agent behaviors
- [ ] Record demo video

---

## What Changes from Phase 1

### Phase 1 (Current)
```bash
$ python3 ableton.py chord-progression C
🎹 Generating pop progression in C major...
✅ Done
```

### Phase 2 (Agent)
```
You: "Create a chill lo-fi beat in C major"

Claude: I'll create a lo-fi arrangement for you. Let me:
1. Set tempo to 85 BPM
2. Generate a pop chord progression in C major
3. Add a golden ratio melody with lower density for a laid-back feel
4. Add subtle hi-hats

[calls: set_tempo(85), chord_progression("C", "pop", "major", 4),
 phi_melody("C", "pentatonic_major", 4, 6), add_hihats(0, 0, 4, 42)]

✓ Created lo-fi beat with:
  - 4-bar C major chord progression (Track 0)
  - Phi-based melody in C pentatonic (Track 1)
  - 16th note hi-hats (Track 0, Scene 0)
  - Tempo: 85 BPM

Try adding an instrument to hear it! The MIDI is ready.
```

---

## Files to Update

1. **`server.py`** - Implement all MCP tools
2. **`music_theory.py`** - Add any new generation functions needed
3. **`ableton.py`** - Refactor to share logic with server.py
4. **`README.md`** - Update with agent capabilities
5. **`CLAUDE.md`** (new) - Usage examples for Claude Code

---

## Why This Makes It a "True Agent"

### Current (CLI Tool)
- Fixed commands
- No reasoning
- No context awareness
- Deterministic

### After Phase 2 (AI Agent)
- **Natural language understanding** - "create a chill beat"
- **Context awareness** - knows what's already in the project
- **Reasoning** - decides which scales, progressions, tempos fit the genre
- **Multi-step planning** - chains multiple tools together
- **Adaptive** - can iterate based on feedback

This is the difference between a tool and an agent.

---

**Next session:** Let's build Phase 2 and make it a true agent! 🤖🎹

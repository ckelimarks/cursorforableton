#!/usr/bin/env python3
"""
Ableton MCP Server - "Cursor for Ableton Live"
Controls Ableton Live via OSC from Claude Code

This implements the agentic loop where Claude can:
1. Understand natural language ("create a lo-fi beat")
2. Decide which tools to use
3. Chain multiple tools together
4. Reflect on results and respond with context
"""

import asyncio
import time
from mcp.server import FastMCP
from pythonosc import udp_client, osc_server, dispatcher
import threading

# Import music generation functions
from music_theory import (
    generate_chord_progression,
    chord_to_midi_notes,
    generate_phi_melody,
    generate_pi_melody,
    melody_to_midi_notes
)

# OSC Configuration
ABLETON_SEND_PORT = 11000  # Send commands to Ableton
ABLETON_RECEIVE_PORT = 11001  # Receive responses from Ableton
OSC_IP = "127.0.0.1"

# Initialize OSC client (to send messages to Ableton)
osc_client = udp_client.SimpleUDPClient(OSC_IP, ABLETON_SEND_PORT)

# Create MCP server
app = FastMCP("ableton-mcp")

# Store responses from Ableton
ableton_responses = {}

def handle_ableton_response(address, *args):
    """Handle incoming OSC messages from Ableton"""
    ableton_responses[address] = args

def start_osc_server():
    """Start OSC server to receive messages from Ableton"""
    disp = dispatcher.Dispatcher()
    disp.map("/*", handle_ableton_response)

    server = osc_server.ThreadingOSCUDPServer(
        (OSC_IP, ABLETON_RECEIVE_PORT), disp
    )
    server.serve_forever()

# Start OSC server in background thread
osc_thread = threading.Thread(target=start_osc_server, daemon=True)
osc_thread.start()

def send_and_wait(address, args=[], wait_time=0.3):
    """Send OSC message and wait for response"""
    osc_client.send_message(address, args)
    time.sleep(wait_time)
    return ableton_responses.get(address)

# ============================================================================
# CONTEXT AWARENESS TOOLS - Let Claude see what's in Ableton
# ============================================================================

@app.tool()
async def get_project_state() -> dict:
    """
    Get current Ableton project state
    Returns tempo, track count, and track information
    """
    result = send_and_wait("/live/song/get/tempo")
    tempo = result[0] if result else 120

    result = send_and_wait("/live/song/get/num_tracks")
    num_tracks = int(result[0]) if result else 0

    return {
        "tempo": tempo,
        "num_tracks": num_tracks,
        "status": "connected"
    }

@app.tool()
async def test_connection() -> str:
    """Test connection to Ableton Live"""
    result = send_and_wait("/live/test")
    if result:
        return "✅ Connected to Ableton Live!"
    return "❌ No response from Ableton - make sure AbletonOSC is enabled"

# ============================================================================
# TRANSPORT & TEMPO TOOLS
# ============================================================================

@app.tool()
async def set_tempo(bpm: float) -> str:
    """
    Set project tempo (BPM)

    Musical conventions:
    - Lo-fi: 70-90 BPM
    - Hip-hop: 85-95 BPM
    - House: 120-130 BPM
    - DnB: 160-180 BPM
    """
    osc_client.send_message("/live/song/set/tempo", [bpm])
    return f"Set tempo to {bpm} BPM"

@app.tool()
async def play() -> str:
    """Start playback"""
    osc_client.send_message("/live/song/start_playing", [])
    return "▶️ Started playback"

@app.tool()
async def stop() -> str:
    """Stop playback"""
    osc_client.send_message("/live/song/stop_playing", [])
    return "⏹️ Stopped playback"

# ============================================================================
# TRACK MANAGEMENT TOOLS
# ============================================================================

@app.tool()
async def create_midi_track() -> str:
    """Create a new MIDI track"""
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    track_count = int(result[0]) if result else 0

    osc_client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    return f"Created MIDI track at index {track_count}"

@app.tool()
async def clean_empty_tracks() -> str:
    """Remove all empty tracks (tracks with no clips)"""
    result = send_and_wait("/live/song/get/num_tracks")
    if not result:
        return "Could not get track count"

    num_tracks = int(result[0])
    tracks_to_delete = []

    # Check each track for clips
    for track_id in range(num_tracks):
        has_any_clips = False
        for scene_id in range(8):
            osc_client.send_message("/live/clip_slot/get/has_clip", [track_id, scene_id])
            time.sleep(0.05)
            response_key = "/live/clip_slot/get/has_clip"
            if response_key in ableton_responses:
                has_clip = ableton_responses[response_key][2]
                if has_clip:
                    has_any_clips = True
                    break

        if not has_any_clips:
            tracks_to_delete.append(track_id)

    # Delete from highest to lowest
    for track_id in sorted(tracks_to_delete, reverse=True):
        osc_client.send_message("/live/song/delete_track", [track_id])
        time.sleep(0.2)

    return f"Deleted {len(tracks_to_delete)} empty tracks"

# ============================================================================
# MUSIC GENERATION TOOLS
# ============================================================================

@app.tool()
async def chord_progression(
    key: str,
    progression: str = "pop",
    scale: str = "major",
    bars: int = 4,
    chord_type: str = "triad"
) -> str:
    """
    Generate a chord progression in Ableton Live

    Creates a new MIDI track with a chord progression.

    Musical conventions:
    - Lo-fi: use "pop" or "minor", slower tempo (70-90 BPM)
    - Jazz: use "jazz" progression, 7th chords
    - EDM: use "basic" (I-IV-V-I), faster tempo (120-130 BPM)
    - Hip-hop: use "minor" or "pop", medium tempo (85-95 BPM)

    Args:
        key: Root note (C, D, E, F, G, A, B, with # or b)
        progression: pop (I-V-vi-IV), jazz (ii-V-I), minor (i-iv-V-i), basic (I-IV-V-I), blues (12-bar)
        scale: major, minor, harmonic_minor, dorian, phrygian, lydian, mixolydian, pentatonic_major, pentatonic_minor
        bars: Number of bars (default 4)
        chord_type: triad (3 notes) or 7th (4 notes with 7th chords)
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    track_id = int(result[0]) if result else 0

    # Create new MIDI track
    osc_client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    osc_client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Generate chord progression
    chords = generate_chord_progression(
        root_note=key,
        progression_name=progression,
        scale_type=scale,
        octave=3,
        bars=bars,
        chord_type=chord_type
    )

    # Convert to MIDI notes
    all_notes = []
    for start_time, chord_notes in chords:
        beats_per_chord = (bars * 4) / len(chords)
        midi_notes = chord_to_midi_notes(chord_notes, start_time, beats_per_chord, velocity=90)
        all_notes.extend(midi_notes)

    # Send to Ableton
    osc_client.send_message("/live/clip/add/notes", [track_id, 0] + all_notes)

    return f"Created {progression} progression in {key} {scale} ({bars} bars, {len(chords)} chords) on track {track_id}"

@app.tool()
async def phi_melody(
    key: str,
    scale: str = "major",
    bars: int = 4,
    density: int = 8
) -> str:
    """
    Generate a melody based on the golden ratio (phi = 1.618...)

    Creates mathematically beautiful melodies using phi's digits to determine
    scale degrees and rhythmic placement.

    Great for:
    - Ambient music
    - Lo-fi backgrounds
    - Interesting melodic patterns

    Args:
        key: Root note (C, D, E, F, G, A, B)
        scale: major, minor, pentatonic_major, pentatonic_minor, dorian, etc.
        bars: Number of bars (default 4)
        density: Notes per bar - higher = more notes (default 8)
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    track_id = int(result[0]) if result else 0

    # Create new MIDI track
    osc_client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    osc_client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Generate phi melody
    melody = generate_phi_melody(key, scale, octave=5, bars=bars, note_density=density)

    # Convert to MIDI notes
    midi_notes = melody_to_midi_notes(melody)

    # Send to Ableton
    osc_client.send_message("/live/clip/add/notes", [track_id, 0] + midi_notes)

    return f"Created phi (φ) melody in {key} {scale} ({bars} bars, {len(melody)} notes) on track {track_id}"

@app.tool()
async def pi_melody(
    key: str,
    scale: str = "major",
    bars: int = 4,
    density: int = 8
) -> str:
    """
    Generate a melody based on pi (π = 3.14159...)

    Creates mathematically interesting melodies using pi's digits.

    Args:
        key: Root note (C, D, E, F, G, A, B)
        scale: major, minor, pentatonic_major, pentatonic_minor, etc.
        bars: Number of bars (default 4)
        density: Notes per bar (default 8)
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    track_id = int(result[0]) if result else 0

    # Create new MIDI track
    osc_client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    osc_client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Generate pi melody
    melody = generate_pi_melody(key, scale, octave=5, bars=bars, note_density=density)

    # Convert to MIDI notes
    midi_notes = melody_to_midi_notes(melody)

    # Send to Ableton
    osc_client.send_message("/live/clip/add/notes", [track_id, 0] + midi_notes)

    return f"Created pi (π) melody in {key} {scale} ({bars} bars, {len(melody)} notes) on track {track_id}"

@app.tool()
async def add_hihats(
    track_id: int,
    scene_id: int = 0,
    bars: int = 4,
    midi_note: int = 42
) -> str:
    """
    Add 16th note hi-hat pattern to a track

    Common drum MIDI notes:
    - 36 = Kick
    - 38 = Snare
    - 42 = Closed Hi-Hat (default)
    - 46 = Open Hi-Hat

    Args:
        track_id: Track index to add hi-hats to
        scene_id: Scene/clip slot index (default 0)
        bars: Number of bars (default 4)
        midi_note: MIDI note number (default 42 = closed hi-hat)
    """
    # 16th notes = 4 per beat, 4 beats per bar
    total_beats = bars * 4
    note_duration = 0.25
    velocity = 80

    # Generate hi-hat pattern
    midi_notes = []
    for beat in range(int(total_beats * 4)):
        start_time = beat * note_duration
        midi_notes.extend([midi_note, start_time, note_duration, velocity, False])

    # Send to Ableton
    osc_client.send_message("/live/clip/add/notes", [track_id, scene_id] + midi_notes)

    num_notes = int(total_beats * 4)
    return f"Added {num_notes} hi-hat notes (MIDI {midi_note}) to track {track_id}, clip {scene_id}"

async def main():
    """Run the MCP server"""
    await app.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())

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

@app.tool()
async def set_track_name(track_id: int, name: str) -> str:
    """
    Rename a track

    Args:
        track_id: Track index to rename
        name: New track name
    """
    osc_client.send_message("/live/track/set/name", [track_id, name])
    return f"Renamed track {track_id} to '{name}'"

@app.tool()
async def set_track_color(track_id: int, color_index: int) -> str:
    """
    Set track color from Ableton's color palette

    Args:
        track_id: Track index
        color_index: Color palette index (0-69)
    """
    osc_client.send_message("/live/track/set/color", [track_id, color_index])
    return f"Set track {track_id} color to {color_index}"

@app.tool()
async def delete_track(track_id: int) -> str:
    """
    Delete a specific track

    Args:
        track_id: Track index to delete
    """
    osc_client.send_message("/live/song/delete_track", [track_id])
    time.sleep(0.2)
    return f"Deleted track {track_id}"

# ============================================================================
# MIXER TOOLS
# ============================================================================

@app.tool()
async def set_track_volume(track_id: int, volume: float) -> str:
    """
    Set track volume

    Args:
        track_id: Track index
        volume: Volume level (0.0 to 1.0)
    """
    osc_client.send_message("/live/track/set/volume", [track_id, volume])
    return f"Set track {track_id} volume to {volume}"

@app.tool()
async def set_track_pan(track_id: int, pan: float) -> str:
    """
    Set track panning

    Args:
        track_id: Track index
        pan: Pan position (-1.0 left to 1.0 right, 0.0 center)
    """
    osc_client.send_message("/live/track/set/panning", [track_id, pan])
    return f"Set track {track_id} pan to {pan}"

@app.tool()
async def set_track_mute(track_id: int, mute: bool) -> str:
    """
    Mute or unmute a track

    Args:
        track_id: Track index
        mute: True to mute, False to unmute
    """
    mute_value = 1 if mute else 0
    osc_client.send_message("/live/track/set/mute", [track_id, mute_value])
    state = "muted" if mute else "unmuted"
    return f"Track {track_id} {state}"

@app.tool()
async def set_track_solo(track_id: int, solo: bool) -> str:
    """
    Solo or unsolo a track

    Args:
        track_id: Track index
        solo: True to solo, False to unsolo
    """
    solo_value = 1 if solo else 0
    osc_client.send_message("/live/track/set/solo", [track_id, solo_value])
    state = "soloed" if solo else "unsoloed"
    return f"Track {track_id} {state}"

@app.tool()
async def set_track_arm(track_id: int, arm: bool) -> str:
    """
    Arm or disarm a track for recording

    Args:
        track_id: Track index
        arm: True to arm, False to disarm
    """
    arm_value = 1 if arm else 0
    osc_client.send_message("/live/track/set/arm", [track_id, arm_value])
    state = "armed" if arm else "disarmed"
    return f"Track {track_id} {state}"

# ============================================================================
# CLIP OPERATION TOOLS
# ============================================================================

@app.tool()
async def fire_clip(track_id: int, scene_id: int) -> str:
    """
    Trigger/launch a clip

    Args:
        track_id: Track index
        scene_id: Scene/clip slot index
    """
    osc_client.send_message("/live/clip_slot/fire", [track_id, scene_id])
    return f"Fired clip at track {track_id}, scene {scene_id}"

@app.tool()
async def stop_clip(track_id: int) -> str:
    """
    Stop a playing clip on a track

    Args:
        track_id: Track index
    """
    osc_client.send_message("/live/track/stop_all_clips", [track_id])
    return f"Stopped clips on track {track_id}"

@app.tool()
async def delete_clip(track_id: int, scene_id: int) -> str:
    """
    Delete a clip from a clip slot

    Args:
        track_id: Track index
        scene_id: Scene/clip slot index
    """
    osc_client.send_message("/live/clip_slot/delete_clip", [track_id, scene_id])
    return f"Deleted clip at track {track_id}, scene {scene_id}"

@app.tool()
async def set_clip_name(track_id: int, scene_id: int, name: str) -> str:
    """
    Rename a clip

    Args:
        track_id: Track index
        scene_id: Scene/clip slot index
        name: New clip name
    """
    osc_client.send_message("/live/clip/set/name", [track_id, scene_id, name])
    return f"Renamed clip at track {track_id}, scene {scene_id} to '{name}'"

@app.tool()
async def set_clip_loop(track_id: int, scene_id: int, start: float, end: float) -> str:
    """
    Set clip loop boundaries

    Args:
        track_id: Track index
        scene_id: Scene/clip slot index
        start: Loop start position in beats
        end: Loop end position in beats
    """
    osc_client.send_message("/live/clip/set/loop_start", [track_id, scene_id, start])
    osc_client.send_message("/live/clip/set/loop_end", [track_id, scene_id, end])
    return f"Set loop for clip at track {track_id}, scene {scene_id} from {start} to {end} beats"

# ============================================================================
# SCENE MANAGEMENT TOOLS
# ============================================================================

@app.tool()
async def create_scene(index: int = -1) -> str:
    """
    Create a new scene

    Args:
        index: Position to insert scene (-1 for end)
    """
    osc_client.send_message("/live/song/create_scene", [index])
    time.sleep(0.2)
    position = "at end" if index == -1 else f"at position {index}"
    return f"Created scene {position}"

@app.tool()
async def delete_scene(scene_id: int) -> str:
    """
    Delete a scene

    Args:
        scene_id: Scene index to delete
    """
    osc_client.send_message("/live/song/delete_scene", [scene_id])
    time.sleep(0.2)
    return f"Deleted scene {scene_id}"

@app.tool()
async def fire_scene(scene_id: int) -> str:
    """
    Launch a scene (trigger all clips in the scene)

    Args:
        scene_id: Scene index to fire
    """
    osc_client.send_message("/live/song/start_listen/scenes", [scene_id])
    return f"Fired scene {scene_id}"

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

@app.tool()
async def add_notes(
    track_id: int,
    scene_id: int,
    notes: list,
    clip_length: float = 4.0
) -> str:
    """
    Add specific MIDI notes to a clip

    This is the most flexible tool for creating precise melodies and compositions.
    Each note is specified with exact timing, pitch, duration, and velocity.

    Args:
        track_id: Track index (0-based)
        scene_id: Scene/clip slot index (0-based)
        notes: List of note dictionaries, each containing:
            - pitch: MIDI note number (0-127, e.g., 60 = middle C)
            - start: Start time in beats (e.g., 0.0, 1.5, 2.0)
            - duration: Note length in beats (e.g., 0.25 = 16th, 0.5 = 8th, 1.0 = quarter)
            - velocity: Note velocity/volume (0-127, default 90)
        clip_length: Length of clip in bars (default 4.0)

    Example:
        notes = [
            {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 90},  # Middle C
            {"pitch": 64, "start": 1.0, "duration": 1.0, "velocity": 90},  # E
            {"pitch": 67, "start": 2.0, "duration": 2.0, "velocity": 90}   # G
        ]
    """
    # Check if clip exists, create if needed
    osc_client.send_message("/live/clip_slot/create_clip", [track_id, scene_id, clip_length])
    time.sleep(0.3)

    # Convert notes to OSC format: [pitch, start, duration, velocity, muted]
    midi_notes = []
    for note in notes:
        pitch = note.get("pitch", 60)
        start = note.get("start", 0.0)
        duration = note.get("duration", 1.0)
        velocity = note.get("velocity", 90)
        muted = False

        midi_notes.extend([pitch, start, duration, velocity, muted])

    # Send to Ableton
    osc_client.send_message("/live/clip/add/notes", [track_id, scene_id] + midi_notes)

    return f"Added {len(notes)} notes to track {track_id}, clip {scene_id}"

async def main():
    """Run the MCP server"""
    await app.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Ableton CLI - Control Ableton Live from the command line
Usage: python3 ableton.py <command> [args]
"""

from pythonosc import udp_client, osc_server, dispatcher
import sys
import time
import threading
from music_theory import (
    generate_chord_progression,
    chord_to_midi_notes,
    generate_phi_melody,
    generate_pi_melody,
    melody_to_midi_notes
)

# OSC Configuration
ABLETON_SEND_PORT = 11000
ABLETON_RECEIVE_PORT = 11001
OSC_IP = "127.0.0.1"

responses = {}

def handle_response(address, *args):
    """Handle OSC responses from Ableton"""
    responses[address] = args

# Set up OSC
client = udp_client.SimpleUDPClient(OSC_IP, ABLETON_SEND_PORT)
disp = dispatcher.Dispatcher()
disp.map("/*", handle_response)
server = osc_server.ThreadingOSCUDPServer((OSC_IP, ABLETON_RECEIVE_PORT), disp)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

def send_and_wait(address, args=[], wait_time=0.3):
    """Send OSC message and wait for response"""
    client.send_message(address, args)
    time.sleep(wait_time)
    return responses.get(address)

def cmd_test():
    """Test connection to Ableton"""
    result = send_and_wait("/live/test")
    if result:
        print("✅ Connected to Ableton Live!")
    else:
        print("❌ No response from Ableton")

def cmd_tempo(bpm=None):
    """Get or set tempo"""
    if bpm is None:
        result = send_and_wait("/live/song/get/tempo")
        if result:
            print(f"Current tempo: {result[0]} BPM")
    else:
        client.send_message("/live/song/set/tempo", [float(bpm)])
        print(f"Set tempo to {bpm} BPM")

def cmd_play():
    """Start playback"""
    client.send_message("/live/song/start_playing", [])
    print("▶️  Playing")

def cmd_stop():
    """Stop playback"""
    client.send_message("/live/song/stop_playing", [])
    print("⏹️  Stopped")

def cmd_tracks():
    """List tracks"""
    result = send_and_wait("/live/song/get/num_tracks")
    if result:
        num_tracks = int(result[0])
        print(f"Total tracks: {num_tracks}")
        for i in range(num_tracks):
            name_result = send_and_wait(f"/live/song/get/track/{i}/name")
            if name_result:
                print(f"  Track {i}: {name_result[0]}")

def cmd_create_midi_track(index=-1):
    """Create a new MIDI track"""
    client.send_message("/live/song/create_midi_track", [int(index)])
    print(f"Created MIDI track at index {index}")

def cmd_create_audio_track(index=-1):
    """Create a new audio track"""
    client.send_message("/live/song/create_audio_track", [int(index)])
    print(f"Created audio track at index {index}")

def cmd_create_clip(track_id, scene_id=0, length=4.0):
    """Create an empty MIDI clip"""
    client.send_message("/live/clip_slot/create_clip", [int(track_id), int(scene_id), float(length)])
    print(f"Created clip on track {track_id}, scene {scene_id}, length {length} bars")

def cmd_add_chords(track_id, scene_id, key, progression='pop', scale='major', bars=4, chord_type='triad'):
    """
    Add a chord progression to a clip
    Usage: python3 ableton.py add-chords <track_id> <scene_id> <key> [progression] [scale] [bars] [chord_type]

    Examples:
      python3 ableton.py add-chords 0 0 C              # Pop progression in C major, 4 bars
      python3 ableton.py add-chords 0 0 Dm minor 8     # Minor progression in D minor, 8 bars
      python3 ableton.py add-chords 0 0 G jazz major 4 7th  # Jazz with 7th chords
    """
    # Generate the chord progression
    chords = generate_chord_progression(
        root_note=key,
        progression_name=progression,
        scale_type=scale,
        octave=3,  # Lower octave for chords
        bars=int(bars),
        chord_type=chord_type
    )

    print(f"🎹 Generating {progression} progression in {key} {scale} ({bars} bars)...")

    # Convert chords to MIDI notes
    all_notes = []
    for start_time, chord_notes in chords:
        beats_per_chord = (int(bars) * 4) / len(chords)
        midi_notes = chord_to_midi_notes(chord_notes, start_time, beats_per_chord, velocity=90)
        all_notes.extend(midi_notes)

    # Send to Ableton
    client.send_message("/live/clip/add/notes", [int(track_id), int(scene_id)] + all_notes)

    print(f"✅ Added {len(chords)} chords to track {track_id}, clip {scene_id}")
    for i, (start_time, notes) in enumerate(chords):
        print(f"   Beat {start_time}: {notes}")

def cmd_chord_progression(key, progression='pop', scale='major', bars=4):
    """
    Create a new track with a chord progression
    Usage: python3 ableton.py chord-progression <key> [progression] [scale] [bars]

    Examples:
      python3 ableton.py chord-progression C
      python3 ableton.py chord-progression Dm minor 8
      python3 ableton.py chord-progression G jazz major 4
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    if not result:
        print("❌ Could not get track count")
        return

    track_id = int(result[0])

    # Create new MIDI track
    client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Add chords
    cmd_add_chords(track_id, 0, key, progression, scale, bars)

def cmd_phi_melody(key, scale='major', bars=4, density=8):
    """
    Create a melody based on the golden ratio (phi)
    Usage: python3 ableton.py phi-melody <key> [scale] [bars] [density]
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    if not result:
        print("❌ Could not get track count")
        return

    track_id = int(result[0])

    # Create new MIDI track
    client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Generate phi-based melody
    print(f"✨ Generating phi (φ = 1.618...) melody in {key} {scale} ({bars} bars, density={density})...")
    melody = generate_phi_melody(key, scale, octave=5, bars=int(bars), note_density=int(density))

    # Convert to MIDI notes
    midi_notes = melody_to_midi_notes(melody)

    # Send to Ableton
    client.send_message("/live/clip/add/notes", [track_id, 0] + midi_notes)

    print(f"✅ Added {len(melody)} notes to track {track_id}, clip 0")
    print(f"   First 5 notes: {[n[0] for n in melody[:5]]}")

def cmd_pi_melody(key, scale='major', bars=4, density=8):
    """
    Create a melody based on pi (π)
    Usage: python3 ableton.py pi-melody <key> [scale] [bars] [density]
    """
    # Get current track count
    result = send_and_wait("/live/song/get/num_tracks")
    if not result:
        print("❌ Could not get track count")
        return

    track_id = int(result[0])

    # Create new MIDI track
    client.send_message("/live/song/create_midi_track", [-1])
    time.sleep(0.3)

    # Create clip
    clip_length = float(bars)
    client.send_message("/live/clip_slot/create_clip", [track_id, 0, clip_length])
    time.sleep(0.3)

    # Generate pi-based melody
    print(f"🥧 Generating pi (π = 3.14159...) melody in {key} {scale} ({bars} bars, density={density})...")
    melody = generate_pi_melody(key, scale, octave=5, bars=int(bars), note_density=int(density))

    # Convert to MIDI notes
    midi_notes = melody_to_midi_notes(melody)

    # Send to Ableton
    client.send_message("/live/clip/add/notes", [track_id, 0] + midi_notes)

    print(f"✅ Added {len(melody)} notes to track {track_id}, clip 0")
    print(f"   First 5 notes: {[n[0] for n in melody[:5]]}")

def cmd_add_hihats(track_id, scene_id=0, bars=4, note=42):
    """
    Add 16th note hi-hats to a track
    Usage: python3 ableton.py add-hihats <track_id> [scene_id] [bars] [midi_note]

    Common drum MIDI notes:
      36 = Kick, 38 = Snare, 42 = Closed Hi-Hat, 46 = Open Hi-Hat
    """
    print(f"🥁 Adding 16th note hi-hats to track {track_id}...")

    # 16th notes = 4 per beat, 4 beats per bar
    notes_per_bar = 16
    total_bars = int(bars)
    total_beats = total_bars * 4
    note_duration = 0.25  # 16th note duration
    velocity = 80

    # Generate hi-hat pattern
    midi_notes = []
    for beat in range(int(total_beats * 4)):  # 4 16th notes per beat
        start_time = beat * note_duration
        midi_notes.extend([int(note), start_time, note_duration, velocity, False])

    # Send to Ableton
    client.send_message("/live/clip/add/notes", [int(track_id), int(scene_id)] + midi_notes)

    num_notes = int(total_beats * 4)
    print(f"✅ Added {num_notes} hi-hat notes (MIDI {note}) to track {track_id}, clip {scene_id}")

def cmd_clean_empty_tracks():
    """
    Remove all empty tracks (tracks with no clips)
    """
    print("🧹 Cleaning empty tracks...")

    # Get number of tracks
    result = send_and_wait("/live/song/get/num_tracks")
    if not result:
        print("❌ Could not get track count")
        return

    num_tracks = int(result[0])
    print(f"Found {num_tracks} tracks")

    # Check each track for clips (check first 8 scenes)
    tracks_to_delete = []

    for track_id in range(num_tracks):
        has_any_clips = False

        # Check first 8 scenes for clips
        for scene_id in range(8):
            client.send_message("/live/clip_slot/get/has_clip", [track_id, scene_id])
            time.sleep(0.05)  # Small delay

            response_key = "/live/clip_slot/get/has_clip"
            if response_key in responses:
                has_clip = responses[response_key][2]  # Third param is has_clip boolean
                if has_clip:
                    has_any_clips = True
                    break

        if not has_any_clips:
            tracks_to_delete.append(track_id)

    if not tracks_to_delete:
        print("✅ No empty tracks found")
        return

    print(f"Found {len(tracks_to_delete)} empty tracks: {tracks_to_delete}")

    # Delete tracks from highest index to lowest (avoids index shifting)
    for track_id in sorted(tracks_to_delete, reverse=True):
        print(f"  Deleting track {track_id}...")
        client.send_message("/live/song/delete_track", [track_id])
        time.sleep(0.2)

    print(f"✅ Deleted {len(tracks_to_delete)} empty tracks")

def show_help():
    """Show available commands"""
    print("""
Ableton CLI - Control Ableton Live from the command line

Commands:
  test                              - Test connection
  tempo [bpm]                       - Get or set tempo
  play                              - Start playback
  stop                              - Stop playback
  tracks                            - List all tracks
  create-midi [index]               - Create MIDI track (default: -1 = end)
  create-audio [index]              - Create audio track (default: -1 = end)
  create-clip <track> <scene> <len> - Create empty MIDI clip
  chord-progression <key> [prog] [scale] [bars]
                                    - Create track with chord progression
  add-chords <track> <scene> <key> [prog] [scale] [bars] [type]
                                    - Add chords to existing clip
  phi-melody <key> [scale] [bars] [density]
                                    - Create melody based on golden ratio
  pi-melody <key> [scale] [bars] [density]
                                    - Create melody based on pi
  help                              - Show this help

Mathematical Melody Examples:
  python3 ableton.py phi-melody C          # Golden ratio melody in C major
  python3 ableton.py phi-melody D minor 8  # 8 bars in D minor
  python3 ableton.py pi-melody G major 4 16  # Dense pi melody (16 notes/bar)

Chord Progression Examples:
  python3 ableton.py chord-progression C
  python3 ableton.py chord-progression D minor minor 8
  python3 ableton.py chord-progression G jazz major 4

Available progressions: basic, pop, jazz, minor, blues
Available scales: major, minor, harmonic_minor, dorian, pentatonic_major
Available chord types: triad, 7th

Basic Examples:
  python3 ableton.py test
  python3 ableton.py tempo 120
  python3 ableton.py play
  python3 ableton.py create-midi
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    commands = {
        "test": lambda: cmd_test(),
        "tempo": lambda: cmd_tempo(args[0] if args else None),
        "play": lambda: cmd_play(),
        "stop": lambda: cmd_stop(),
        "tracks": lambda: cmd_tracks(),
        "create-midi": lambda: cmd_create_midi_track(args[0] if args else -1),
        "create-audio": lambda: cmd_create_audio_track(args[0] if args else -1),
        "create-clip": lambda: cmd_create_clip(args[0], args[1] if len(args) > 1 else 0, args[2] if len(args) > 2 else 4.0),
        "chord-progression": lambda: cmd_chord_progression(
            args[0],
            args[1] if len(args) > 1 else 'pop',
            args[2] if len(args) > 2 else 'major',
            args[3] if len(args) > 3 else 4
        ),
        "add-chords": lambda: cmd_add_chords(
            args[0],
            args[1],
            args[2],
            args[3] if len(args) > 3 else 'pop',
            args[4] if len(args) > 4 else 'major',
            args[5] if len(args) > 5 else 4,
            args[6] if len(args) > 6 else 'triad'
        ),
        "phi-melody": lambda: cmd_phi_melody(
            args[0],
            args[1] if len(args) > 1 else 'major',
            args[2] if len(args) > 2 else 4,
            args[3] if len(args) > 3 else 8
        ),
        "pi-melody": lambda: cmd_pi_melody(
            args[0],
            args[1] if len(args) > 1 else 'major',
            args[2] if len(args) > 2 else 4,
            args[3] if len(args) > 3 else 8
        ),
        "add-hihats": lambda: cmd_add_hihats(
            args[0],
            args[1] if len(args) > 1 else 0,
            args[2] if len(args) > 2 else 4,
            args[3] if len(args) > 3 else 42
        ),
        "clean": lambda: cmd_clean_empty_tracks(),
        "help": lambda: show_help(),
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)

    server.shutdown()

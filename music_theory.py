"""
Music Theory Engine for Ableton MCP
Handles scales, chords, progressions, and MIDI note generation
"""

# MIDI note numbers (C4 = 60 is middle C)
NOTES = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

# Scale intervals (semitones from root)
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
}

# Chord intervals (scale degrees, 0-indexed)
CHORDS = {
    'major': [0, 2, 4],           # I (1-3-5)
    'minor': [0, 2, 4],           # i
    'diminished': [0, 2, 4],      # dim
    'maj7': [0, 2, 4, 6],         # Imaj7
    'min7': [0, 2, 4, 6],         # imin7
    '7': [0, 2, 4, 6],            # I7 (dominant)
    'sus2': [0, 1, 4],            # sus2
    'sus4': [0, 3, 4],            # sus4
}

# Common chord progressions (scale degrees, 1-indexed)
PROGRESSIONS = {
    'basic': [1, 4, 5, 1],              # I-IV-V-I
    'pop': [1, 5, 6, 4],                # I-V-vi-IV
    'jazz': [2, 5, 1, 1],               # ii-V-I-I
    'minor': [1, 4, 5, 1],              # i-iv-V-i
    'blues': [1, 1, 4, 4, 1, 1, 5, 4, 1, 5],  # 12-bar blues
}

def note_to_midi(note_name, octave=4):
    """Convert note name + octave to MIDI number"""
    if note_name not in NOTES:
        raise ValueError(f"Invalid note: {note_name}")
    return NOTES[note_name] + (octave * 12) + 12

def get_scale(root_note, scale_type='major', octave=4):
    """Get all notes in a scale"""
    root_midi = note_to_midi(root_note, octave)
    intervals = SCALES.get(scale_type, SCALES['major'])
    return [root_midi + interval for interval in intervals]

def get_chord(root_note, chord_type='major', scale_type='major', octave=4):
    """Get notes for a chord based on scale degrees"""
    scale = get_scale(root_note, scale_type, octave)

    # Map chord types to scale degrees
    if chord_type == 'major':
        return [scale[0], scale[2], scale[4]]  # 1-3-5
    elif chord_type == 'minor':
        # Lower the 3rd
        return [scale[0], scale[2] - 1, scale[4]]
    elif chord_type == 'maj7':
        return [scale[0], scale[2], scale[4], scale[6]]
    elif chord_type == 'min7':
        return [scale[0], scale[2] - 1, scale[4], scale[6] - 1]
    elif chord_type == '7':  # Dominant 7
        return [scale[0], scale[2], scale[4], scale[6] - 1]
    elif chord_type == 'diminished':
        return [scale[0], scale[2] - 1, scale[4] - 1]
    else:
        return [scale[0], scale[2], scale[4]]

def get_chord_from_degree(degree, root_note, scale_type='major', octave=4, chord_type='triad'):
    """
    Get chord for a scale degree (1-7)
    Automatically determines major/minor based on scale harmonization
    """
    scale = get_scale(root_note, scale_type, octave)
    degree_index = degree - 1  # Convert to 0-indexed

    if degree_index < 0 or degree_index >= len(scale):
        raise ValueError(f"Invalid degree: {degree}")

    chord_root = scale[degree_index]

    # Build chord using scale degrees
    if chord_type == 'triad':
        notes = [
            chord_root,
            scale[(degree_index + 2) % len(scale)],
            scale[(degree_index + 4) % len(scale)]
        ]
    elif chord_type == '7th':
        notes = [
            chord_root,
            scale[(degree_index + 2) % len(scale)],
            scale[(degree_index + 4) % len(scale)],
            scale[(degree_index + 6) % len(scale)]
        ]
    else:
        notes = [chord_root]

    return notes

def generate_chord_progression(root_note, progression_name='pop', scale_type='major',
                               octave=4, bars=4, chord_type='triad'):
    """
    Generate a chord progression
    Returns list of (start_time, chord_notes) tuples
    """
    progression = PROGRESSIONS.get(progression_name, PROGRESSIONS['pop'])

    # Calculate beats per chord
    beats_per_bar = 4
    total_beats = bars * beats_per_bar
    beats_per_chord = total_beats / len(progression)

    chords = []
    for i, degree in enumerate(progression):
        start_time = i * beats_per_chord
        chord_notes = get_chord_from_degree(degree, root_note, scale_type, octave, chord_type)
        chords.append((start_time, chord_notes))

    return chords

def chord_to_midi_notes(chord_notes, start_time, duration=4.0, velocity=100):
    """
    Convert chord to MIDI note parameters for OSC
    Returns flat list: [pitch1, start1, dur1, vel1, mute1, pitch2, start2, ...]
    """
    notes = []
    for pitch in chord_notes:
        notes.extend([pitch, start_time, duration, velocity, False])
    return notes

def generate_phi_melody(root_note, scale_type='major', octave=4, bars=4, note_density=8):
    """
    Generate a melody based on the golden ratio (phi = 1.618...)
    Uses phi's digits to determine scale degrees and rhythmic placement

    Args:
        root_note: Root note (e.g., 'C', 'D')
        scale_type: Type of scale
        octave: Starting octave
        bars: Number of bars
        note_density: Notes per bar (higher = more notes)

    Returns:
        List of (pitch, start_time, duration, velocity) tuples
    """
    import math

    # Golden ratio and its digits
    phi = (1 + math.sqrt(5)) / 2  # 1.618033988749...
    phi_str = str(phi).replace('.', '')

    scale = get_scale(root_note, scale_type, octave)
    scale_extended = scale + get_scale(root_note, scale_type, octave + 1)  # Two octaves

    beats_per_bar = 4
    total_beats = bars * beats_per_bar
    notes_per_beat = note_density / beats_per_bar
    total_notes = int(bars * note_density)

    melody = []

    for i in range(total_notes):
        # Use phi digits to select scale degrees
        digit_index = i % len(phi_str)
        digit = int(phi_str[digit_index])

        # Map digit (0-9) to scale degree
        scale_degree = digit % len(scale_extended)
        pitch = scale_extended[scale_degree]

        # Calculate timing using phi ratio for interesting rhythm
        start_time = (i / total_notes) * total_beats

        # Duration based on next digit (creates rhythmic variation)
        next_digit = int(phi_str[(digit_index + 1) % len(phi_str)])
        duration = (next_digit / 10) * (total_beats / total_notes) * 2  # Varies duration
        duration = max(0.25, min(duration, 2.0))  # Clamp to reasonable range

        # Velocity variation based on phi
        velocity = 60 + int(phi * digit * 4) % 40  # 60-100 range

        melody.append((pitch, start_time, duration, velocity))

    return melody

def generate_pi_melody(root_note, scale_type='major', octave=4, bars=4, note_density=8):
    """
    Generate a melody based on pi (3.14159...)
    Uses pi's digits to create melodic patterns
    """
    import math

    # Pi and its digits
    pi_str = str(math.pi).replace('.', '')

    scale = get_scale(root_note, scale_type, octave)
    scale_extended = scale + get_scale(root_note, scale_type, octave + 1)

    beats_per_bar = 4
    total_beats = bars * beats_per_bar
    total_notes = int(bars * note_density)

    melody = []

    for i in range(total_notes):
        # Use pi digits to select scale degrees
        digit_index = i % len(pi_str)
        digit = int(pi_str[digit_index])

        # Map digit (0-9) to scale degree with some chromatic passing
        scale_degree = digit % len(scale_extended)
        pitch = scale_extended[scale_degree]

        # Timing
        start_time = (i / total_notes) * total_beats

        # Duration varies with pi
        next_digit = int(pi_str[(digit_index + 1) % len(pi_str)])
        duration = (next_digit / 10) * (total_beats / total_notes) * 1.5
        duration = max(0.25, min(duration, 1.5))

        # Velocity from pi
        velocity = 70 + int(digit * 3) % 30  # 70-100 range

        melody.append((pitch, start_time, duration, velocity))

    return melody

def melody_to_midi_notes(melody):
    """
    Convert melody to MIDI note parameters for OSC
    melody: List of (pitch, start_time, duration, velocity) tuples
    Returns flat list: [pitch1, start1, dur1, vel1, mute1, ...]
    """
    notes = []
    for pitch, start_time, duration, velocity in melody:
        notes.extend([pitch, start_time, duration, velocity, False])
    return notes

if __name__ == "__main__":
    # Test the music theory engine
    print("Testing Music Theory Engine\n")

    # Test scale generation
    c_major = get_scale('C', 'major', 4)
    print(f"C Major scale: {c_major}")

    # Test chord generation
    c_major_chord = get_chord('C', 'major', 'major', 4)
    print(f"C Major chord: {c_major_chord}")

    # Test progression generation
    progression = generate_chord_progression('C', 'pop', 'major', 4, bars=4)
    print(f"\nPop progression in C Major (4 bars):")
    for start_time, notes in progression:
        print(f"  Beat {start_time}: {notes}")

    # Test MIDI note formatting
    midi_notes = chord_to_midi_notes([60, 64, 67], 0.0, 4.0, 100)
    print(f"\nMIDI notes for C Major: {midi_notes}")

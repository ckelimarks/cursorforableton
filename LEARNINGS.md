# Prototype Hour #02 - Learnings

## Session: January 15, 2026

### What Worked ✅
- OSC communication with Ableton Live via AbletonOSC
- Creating MIDI tracks programmatically
- Creating clips on tracks
- Adding MIDI notes to clips
- Chord progression generation (pop, jazz, minor, basic, blues)
- Music theory engine (scales, chord harmonization)
- Transport control (play/stop)
- Tempo control

### Issues Discovered 🔍

#### 1. Play Command Behavior
**Issue:** `python3 ableton.py play` enables global play, not the specific clip
- When you create a clip and call play(), it starts global transport
- In clip view, you don't hear the specific clip unless it's triggered
- **Need:** Clip triggering command (`/live/clip/fire` or similar)

#### 2. No Sound from MIDI Tracks
**Issue:** Created MIDI tracks are empty (no instrument loaded)
- Generated MIDI notes exist but produce no sound
- Need to load a default instrument (Operator, Simpler, etc.)
- **Need:** Device loading command (`/live/track/device/add` or similar)

#### 3. Instrument Loading
**Workaround for now:** Manually load an instrument on the track
**TODO:** Add automatic instrument loading to `chord-progression` command

### Next Steps
- Add clip triggering (fire specific clips)
- Add device/instrument loading
- Create melody generator based on mathematical constants (phi, pi)
- Add rhythm patterns
- Add bassline generator

### Commands That Work
```bash
python3 ableton.py test                    # ✅ Test connection
python3 ableton.py tracks                  # ✅ List tracks
python3 ableton.py create-midi             # ✅ Create MIDI track
python3 ableton.py chord-progression C     # ✅ Create chord progression
python3 ableton.py chord-progression D minor minor 8  # ✅ 8-bar minor
python3 ableton.py play                    # ✅ Start transport (but not specific clip)
python3 ableton.py stop                    # ✅ Stop transport
python3 ableton.py tempo 120               # ✅ Set BPM
```

### Tech Stack Working
- Python 3.10
- AbletonOSC (MIDI Remote Script)
- python-osc library
- Custom music theory engine
- OSC ports: 11000 (send), 11001 (receive)

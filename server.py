#!/usr/bin/env python3
"""
Ableton MCP Server - "Cursor for Ableton Live"
Controls Ableton Live via OSC from Claude Code
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pythonosc import udp_client, osc_server, dispatcher
import threading

# OSC Configuration
ABLETON_SEND_PORT = 11000  # Send commands to Ableton
ABLETON_RECEIVE_PORT = 11001  # Receive responses from Ableton
OSC_IP = "127.0.0.1"

# Initialize OSC client (to send messages to Ableton)
osc_client = udp_client.SimpleUDPClient(OSC_IP, ABLETON_SEND_PORT)

# Create MCP server
app = Server("ableton-mcp")

# Store responses from Ableton
ableton_responses = {}

def handle_ableton_response(address, *args):
    """Handle incoming OSC messages from Ableton"""
    ableton_responses[address] = args
    print(f"Received from Ableton: {address} {args}")

def start_osc_server():
    """Start OSC server to receive messages from Ableton"""
    disp = dispatcher.Dispatcher()
    disp.map("/*", handle_ableton_response)  # Catch all messages

    server = osc_server.ThreadingOSCUDPServer(
        (OSC_IP, ABLETON_RECEIVE_PORT), disp
    )
    print(f"OSC Server listening on {OSC_IP}:{ABLETON_RECEIVE_PORT}")
    server.serve_forever()

# Start OSC server in background thread
osc_thread = threading.Thread(target=start_osc_server, daemon=True)
osc_thread.start()

@app.tool()
def test_connection() -> str:
    """Test connection to Ableton Live"""
    osc_client.send_message("/live/test", [])
    asyncio.sleep(0.5)  # Wait for response
    if "/live/test" in ableton_responses:
        return "✅ Connected to Ableton Live!"
    return "❌ No response from Ableton - make sure AbletonOSC is enabled"

@app.tool()
def get_tempo() -> str:
    """Get current tempo (BPM)"""
    osc_client.send_message("/live/song/get/tempo", [])
    asyncio.sleep(0.2)
    if "/live/song/get/tempo" in ableton_responses:
        tempo = ableton_responses["/live/song/get/tempo"][0]
        return f"Current tempo: {tempo} BPM"
    return "Could not get tempo"

@app.tool()
def set_tempo(bpm: float) -> str:
    """Set tempo (BPM)"""
    osc_client.send_message("/live/song/set/tempo", [bpm])
    return f"Set tempo to {bpm} BPM"

@app.tool()
def create_midi_track(index: int = -1) -> str:
    """Create a new MIDI track at the specified index (-1 = end of list)"""
    osc_client.send_message("/live/song/create_midi_track", [index])
    return f"Created MIDI track at index {index}"

@app.tool()
def play() -> str:
    """Start playback"""
    osc_client.send_message("/live/song/start_playing", [])
    return "▶️ Started playback"

@app.tool()
def stop() -> str:
    """Stop playback"""
    osc_client.send_message("/live/song/stop_playing", [])
    return "⏹️ Stopped playback"

@app.tool()
def get_tracks() -> str:
    """Get list of all tracks"""
    osc_client.send_message("/live/song/get/num_tracks", [])
    asyncio.sleep(0.2)
    if "/live/song/get/num_tracks" in ableton_responses:
        num_tracks = ableton_responses["/live/song/get/num_tracks"][0]
        return f"Total tracks: {num_tracks}"
    return "Could not get tracks"

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

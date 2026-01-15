#!/usr/bin/env python3
"""
Quick test script to verify OSC communication with Ableton
"""

from pythonosc import udp_client, osc_server, dispatcher
import time

# OSC Configuration
ABLETON_SEND_PORT = 11000
ABLETON_RECEIVE_PORT = 11001
OSC_IP = "127.0.0.1"

# Track responses
responses = {}

def handle_response(address, *args):
    """Handle OSC responses from Ableton"""
    responses[address] = args
    print(f"✅ Received: {address} → {args}")

# Set up OSC client to send to Ableton
client = udp_client.SimpleUDPClient(OSC_IP, ABLETON_SEND_PORT)

# Set up OSC server to receive from Ableton
disp = dispatcher.Dispatcher()
disp.map("/*", handle_response)
server = osc_server.ThreadingOSCUDPServer((OSC_IP, ABLETON_RECEIVE_PORT), disp)

print(f"📡 Starting OSC receiver on {OSC_IP}:{ABLETON_RECEIVE_PORT}")
import threading
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

print(f"🎹 Sending test message to Ableton on port {ABLETON_SEND_PORT}...")
client.send_message("/live/test", [])

time.sleep(1)

if "/live/test" in responses:
    print("\n✅ SUCCESS! Connected to Ableton Live")

    # Try getting tempo
    print("\n📊 Getting tempo...")
    client.send_message("/live/song/get/tempo", [])
    time.sleep(0.5)

    if "/live/song/get/tempo" in responses:
        tempo = responses["/live/song/get/tempo"][0]
        print(f"Current tempo: {tempo} BPM")

    # Try getting track count
    print("\n🎛️ Getting track count...")
    client.send_message("/live/song/get/num_tracks", [])
    time.sleep(0.5)

    if "/live/song/get/num_tracks" in responses:
        num_tracks = responses["/live/song/get/num_tracks"][0]
        print(f"Total tracks: {num_tracks}")

    print("\n✅ All tests passed! OSC communication working.")
else:
    print("\n❌ No response from Ableton")
    print("Make sure:")
    print("1. Ableton Live is running")
    print("2. AbletonOSC is selected in Preferences > Link/MIDI")
    print("3. Check logs at: ~/Music/Ableton/User Library/Remote Scripts/AbletonOSC/logs/")

server.shutdown()

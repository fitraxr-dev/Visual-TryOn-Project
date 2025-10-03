#!/usr/bin/env python3
"""
Test client untuk Webcam WebSocket Server
"""

import asyncio
import websockets
import json

async def test_websocket_connection():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for metadata message
            message = await websocket.recv()
            if isinstance(message, str):
                metadata = json.loads(message)
                print(f"📊 Received metadata: {metadata}")
            
            # Receive a few frames
            frame_count = 0
            while frame_count < 3:
                message = await websocket.recv()
                if isinstance(message, bytes):
                    frame_count += 1
                    print(f"🎥 Received frame {frame_count}, size: {len(message)} bytes")
                
            print("✅ Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
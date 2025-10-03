# WebSocket Protocol Documentation

## Overview

Dokumentasi ini menjelaskan protokol komunikasi antara Godot WebSocket client dan Python server untuk streaming webcam.

## Connection Setup

### Server Configuration

- **Host**: `localhost` (127.0.0.1)
- **Port**: `8765`
- **Protocol**: WebSocket (ws://)
- **URL**: `ws://localhost:8765`

### Client Connection Process

1. Client membuat instance `WebSocketPeer`
2. Client memanggil `connect_to_url("ws://localhost:8765")`
3. Client melakukan polling dengan `socket.poll()` di `_process()`
4. Client memonitor state dengan `get_ready_state()`

## Message Types

### 1. Text Messages (JSON Metadata)

Dikirim oleh server untuk memberikan informasi tentang stream:

```json
{
  "width": 640,
  "height": 480,
  "fps": 30,
  "format": "MJPEG",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Godot Handling:**

```gdscript
var text = packet.get_string_from_utf8()
if text != "" and text.length() > 0:
    var json = JSON.new()
    var parse_result = json.parse(text)
    if parse_result == OK:
        var data = json.data
        print("Metadata: ", data)
```

### 2. Binary Messages (JPEG Frames)

Dikirim oleh server berisi frame webcam dalam format JPEG bytes.

**Godot Handling:**

```gdscript
func _process_jpeg_frame(data: PackedByteArray):
    var image = Image.new()
    var error = image.load_jpg_from_buffer(data)
    if error == OK:
        var texture = ImageTexture.new()
        texture.set_image(image)
        texture_rect.texture = texture
```

## State Management

### WebSocket States

- **STATE_CONNECTING**: Sedang mencoba menghubungkan
- **STATE_OPEN**: Koneksi berhasil, siap menerima data
- **STATE_CLOSING**: Koneksi sedang ditutup
- **STATE_CLOSED**: Koneksi telah ditutup

### Client State Handling

```gdscript
match websocket_client.get_ready_state():
    WebSocketPeer.STATE_OPEN:
        # Handle incoming packets
        while websocket_client.get_available_packet_count():
            _handle_packet()

    WebSocketPeer.STATE_CLOSED:
        # Handle disconnection
        _on_disconnected()
```

## Error Handling

### Common Issues

1. **Connection Failed**

   - Server tidak berjalan
   - Port salah atau sudah digunakan
   - Firewall memblokir koneksi

2. **JPEG Decode Error**

   - Data corrupt atau tidak lengkap
   - Format tidak valid
   - Buffer kosong

3. **Network Issues**
   - Timeout
   - Packet loss
   - Network latency

### Error Codes

```gdscript
func _on_websocket_closed():
    var code = websocket_client.get_close_code()
    var reason = websocket_client.get_close_reason()

    match code:
        1000: print("Normal closure")
        1001: print("Going away")
        1008: print("Policy violation")
        1011: print("Internal server error")
```

## Performance Considerations

### Frame Rate Optimization

- Server mengirim frame dengan target FPS (default: 30)
- Client memproses frame sesuai kemampuan
- Godot `_process()` dipanggil setiap frame (60 FPS default)

### Memory Management

- `Image` dan `ImageTexture` dibuat ulang setiap frame
- Godot melakukan garbage collection otomatis
- Untuk optimasi, bisa reuse texture object

### Network Optimization

- JPEG compression mengurangi ukuran data
- WebSocket binary frame lebih efisien
- Consider frame skipping jika network lambat

## Debugging Tips

### Enable Verbose Logging

```gdscript
func _handle_packet():
    var packet = websocket_client.get_packet()
    print("Packet size: ", packet.size())
    # ... rest of handling
```

### Monitor Connection Status

```gdscript
func _process(_delta):
    var state = websocket_client.get_ready_state()
    print("WebSocket state: ", state)
```

### Test with Simple Server

Gunakan scene `test_websocket.tscn` untuk debugging koneksi dasar.

## Security Notes

### Local Development

- Koneksi ke `localhost` relatif aman
- Tidak ada enkripsi (ws:// bukan wss://)
- Cocok untuk development dan testing

### Production Considerations

- Gunakan `wss://` untuk HTTPS
- Implement authentication jika diperlukan
- Validate semua input dari server
- Consider rate limiting

## Example Implementation

### Minimal WebSocket Client

```gdscript
extends Control

var websocket = WebSocketPeer.new()
@onready var texture_rect = $TextureRect

func _ready():
    websocket.connect_to_url("ws://localhost:8765")

func _process(_delta):
    websocket.poll()
    if websocket.get_ready_state() == WebSocketPeer.STATE_OPEN:
        while websocket.get_available_packet_count():
            var packet = websocket.get_packet()
            var image = Image.new()
            if image.load_jpg_from_buffer(packet) == OK:
                var texture = ImageTexture.new()
                texture.set_image(image)
                texture_rect.texture = texture
```

### Server Python Minimal Example

```python
import asyncio
import websockets
import cv2

async def serve_webcam(websocket, path):
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                await websocket.send(buffer.tobytes())
            await asyncio.sleep(1/30)  # 30 FPS
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        cap.release()

start_server = websockets.serve(serve_webcam, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

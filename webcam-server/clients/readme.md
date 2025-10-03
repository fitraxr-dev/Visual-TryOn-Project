# Client Documentation

Folder ini berisi berbagai implementasi client untuk testing dan integrasi dengan Webcam WebSocket Server.

## Browser Test Client

### Lokasi

`browser_test/` - Client HTML/JavaScript untuk testing di browser

### Fitur

- Connect/disconnect ke WebSocket server
- Menampilkan metadata server (resolusi, FPS)
- Menampilkan video stream real-time
- Interface sederhana untuk testing

### Penggunaan

1. Pastikan server berjalan (`python server/server.py`)
2. Buka `browser_test/index.html` di browser
3. Klik "Connect to WebSocket"
4. Video stream akan muncul

## Future Clients

### Godot Engine Client

- Akan diimplementasi untuk integrasi game engine
- Menggunakan WebSocketClient built-in Godot
- Handle binary frame dan JSON metadata
- Convert ke ImageTexture untuk rendering

### Python Client

- Client Python untuk testing atau aplikasi desktop
- Menggunakan library `websockets`
- Dapat digunakan untuk save video atau processing

### Mobile Client

- React Native atau Flutter
- Real-time video streaming ke mobile device
- Touch controls untuk konfigurasi

## Protokol Komunikasi

### Server ke Client

**Metadata (JSON Text Message):**

```json
{
  "type": "meta",
  "width": 640,
  "height": 480,
  "fps": 15
}
```

**Frame Data (Binary Message):**

- Raw JPEG binary data
- Ukuran bervariasi tergantung kompleksitas frame
- Format: bytes dari cv2.imencode()

### Client ke Server

**Konfigurasi (JSON Text Message):**

```json
{
  "type": "config",
  "resolution": [1280, 720],
  "fps": 30,
  "jpeg_quality": 90
}
```

## Error Handling

### Connection Errors

- Server penuh (max clients reached)
- Network issues
- Authentication failures (future)

### Data Errors

- Corrupt frame data
- Invalid JSON messages
- Unsupported configurations

## Performance Tips

### Bandwidth Optimization

- Turunkan resolusi untuk koneksi lambat
- Adjust JPEG quality sesuai kebutuhan
- Monitor frame rate dan adjust FPS

### Client Implementation

- Buffer frames untuk smooth playback
- Handle reconnection otomatis
- Implement backpressure handling

## Development

### Testing New Clients

1. Implement WebSocket connection ke `ws://localhost:8765`
2. Handle text message untuk metadata
3. Handle binary message untuk frame data
4. Test dengan berbagai kondisi network
5. Implement error handling dan reconnection

### Debugging

- Gunakan browser developer tools untuk WebSocket debugging
- Check server logs untuk connection issues
- Monitor bandwidth usage
- Test dengan multiple clients simultaneously

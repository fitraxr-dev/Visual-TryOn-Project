# Quick Start Guide

## Panduan Cepat Menjalankan Webcam Client

### Step 1: Setup Server Python
```bash
cd webcam-server
pip install -r requirements.txt
python server/server.py
```

Server akan berjalan di `ws://localhost:8765`

### Step 2: Setup Godot Project
1. Buka Godot Editor
2. Import project dari folder `godot_virtual_tryon/`
3. Pastikan main scene sudah di-set ke `webcam_standalone.tscn`

### Step 3: Run
Tekan `F5` atau klik "Play Project"

## Hasil yang Diharapkan
- Status "Connected" muncul di layar
- Video webcam ditampilkan dalam window Godot
- Console menampilkan log koneksi dan frame decode

## Troubleshooting

### ❌ WebSocket Error Code -1
**Masalah**: Connection failed immediately 
**Kemungkinan Penyebab**:
1. Server Python tidak berjalan
2. Port 8765 digunakan aplikasi lain
3. Firewall memblokir koneksi
4. Server crash atau tidak merespons

**Solusi Step-by-Step**:
1. **Check server Python**:
   ```bash
   cd webcam-server
   python server/server.py
   ```
   Output yang benar: `Server started on ws://localhost:8765`

2. **Test port availability**:
   ```bash
   netstat -an | findstr 8765
   ```
   Harus muncul: `TCP 0.0.0.0:8765 LISTENING`

3. **Gunakan Debug Scene**:
   - Set main scene ke `debug_websocket.tscn`
   - Klik tombol "Connect" 
   - Lihat log detail di scene

4. **Check server logs**:
   - Lihat terminal server Python
   - Cari error atau crash messages

### ❌ Status "Connection Failed"
**Masalah**: Server Python tidak berjalan atau port salah
**Solusi**: 
- Check apakah server Python berjalan di terminal
- Pastikan tidak ada aplikasi lain yang menggunakan port 8765
- Restart server jika perlu

### ❌ Status "Connected" tapi tidak ada video
**Masalah**: Server mengirim data tapi JPEG decode gagal
**Solusi**:
- Check console Godot untuk error decode
- Pastikan webcam connected dan berfungsi
- Restart server Python

### ❌ Error "Failed to decode JPEG"
**Masalah**: Data corrupt atau format tidak sesuai
**Solusi**:
- Check server Python mengirim data JPEG valid
- Test dengan scene `debug_websocket.tscn` untuk logging detail

### ❌ Lag atau frame drop
**Masalah**: Network latency atau performance issue
**Solusi**:
- Kurangi FPS di server (edit `TARGET_FPS`)
- Kurangi resolusi webcam
- Check CPU usage

## Quick Commands

### Start Python Server
```bash
cd webcam-server && python server/server.py
```

### Check Server Status
```bash
curl -I http://localhost:8765
# atau gunakan browser: ws://localhost:8765
```

### Test WebSocket Connection
Gunakan browser developer tools:
```javascript
const ws = new WebSocket('ws://localhost:8765');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Received:', e.data);
```

## Alternative Scenes

### Debug Scene (RECOMMENDED untuk troubleshooting)
Set main scene ke: `debug_websocket.tscn`
- Detailed logging dengan timestamp
- Manual connect/disconnect buttons
- Connection retry logic dengan diagnostic
- Real-time error messages dan troubleshooting tips

### Test Scene (Recommended untuk debugging)
Set main scene ke: `test_websocket.tscn`
- Ada tombol Connect/Disconnect
- Manual control koneksi
- Berguna untuk testing

### Autoload Version
Set main scene ke: `webcam_view.tscn`
- Menggunakan autoload `WebcamClient`
- Lebih modular tapi kompleks
- Berguna untuk multi-scene project

### Standalone Version (Default)
Set main scene ke: `webcam_standalone.tscn`
- Semua logic dalam satu file
- Auto-retry connection pada failure
- Mudah dipahami dan di-debug
- Direkomendasikan untuk production

## Performance Settings

### Godot Project Settings
- **Target FPS**: Default 60 (Project Settings > Rendering > Max FPS)
- **VSync**: Off untuk testing (Project Settings > Rendering > VSync Mode)

### Server Python Settings
Edit `webcam-server/server/config.py`:
```python
TARGET_FPS = 30        # Kurangi untuk performance
CAMERA_WIDTH = 640     # Kurangi untuk network efficiency  
CAMERA_HEIGHT = 480    # Kurangi untuk network efficiency
```

## Next Steps

1. **Customize UI**: Edit scene untuk menambah kontrol atau info display
2. **Add Features**: Implement zoom, pan, filters
3. **Network**: Test dengan remote server (ganti localhost)
4. **Security**: Implement authentication jika diperlukan
5. **Recording**: Add feature untuk save/record video frames

---

💡 **Tip**: Selalu jalankan server Python dulu sebelum menjalankan Godot client!
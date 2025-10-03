# Webcam WebSocket Server

Proyek Python untuk streaming video webcam melalui WebSocket dengan dukungan binary frame dan JSON metadata.

## Fitur

- Stream video webcam real-time melalui WebSocket
- Encoding frame ke JPEG untuk efisiensi
- Binary frame transfer untuk performa optimal
- JSON metadata untuk informasi tambahan
- Multi-client support dengan broadcast
- Interface browser test untuk development
- Arsitektur yang mudah diintegrasikan dengan Godot Engine

## Instalasi

### 1. Setup Virtual Environment (Opsional tapi Disarankan)

```bash
python -m venv webcam-env
webcam-env\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Penggunaan

### 1. Menjalankan Server

```bash
python server/server.py
```

Server akan berjalan di `ws://localhost:8765`

### 2. Testing dengan Browser

1. Buka file `clients/browser_test/index.html` di browser
2. Klik tombol "Connect to WebSocket"
3. Video stream dari webcam akan muncul di halaman

## Struktur Proyek

```
├── server/
│   ├── __init__.py           # Package marker
│   ├── config.py            # Konfigurasi server
│   ├── server.py            # WebSocket server utama
│   ├── camera.py            # Pengelolaan webcam
│   └── utils.py             # Utility functions
├── clients/
│   ├── browser_test/
│   │   ├── index.html       # Interface test browser
│   │   └── client.js        # JavaScript client
│   └── readme.md           # Dokumentasi client
├── requirements.txt         # Dependencies Python
└── README.md               # Dokumentasi utama
```

## Protokol Komunikasi

### Pesan dari Server ke Client

1. **JSON Metadata** (text message):

   ```json
   {
     "type": "meta",
     "width": 640,
     "height": 480,
     "fps": 15
   }
   ```

2. **Frame JPEG** (binary message):
   - Raw binary data dari frame JPEG yang di-encode

### Pesan dari Client ke Server

- JSON message untuk konfigurasi (opsional):
  ```json
  {
    "type": "config",
    "fps": 30,
    "resolution": [1280, 720]
  }
  ```

## Konfigurasi

Edit `server/config.py` untuk mengubah:

- Port server
- Resolusi video
- FPS target
- Kualitas JPEG encoding

## Integrasi Godot Engine

Server ini dirancang untuk mudah diintegrasikan dengan Godot Engine:

1. Gunakan WebSocketClient di Godot
2. Connect ke `ws://localhost:8765`
3. Handle binary message untuk frame
4. Handle text message untuk metadata
5. Convert binary ke ImageTexture di Godot

## Troubleshooting

### Webcam tidak terdeteksi

- Pastikan webcam terhubung dan tidak digunakan aplikasi lain
- Coba ubah camera index di `config.py`

### Koneksi WebSocket gagal

- Pastikan server berjalan di port yang benar
- Check firewall settings
- Pastikan tidak ada aplikasi lain yang menggunakan port 8765

### Performance issues

- Kurangi FPS di config.py
- Turunkan resolusi video
- Kurangi kualitas JPEG encoding

## Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request

## Lisensi

MIT License

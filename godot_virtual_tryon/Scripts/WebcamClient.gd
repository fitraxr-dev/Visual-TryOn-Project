class_name WebcamClient
extends Node

"""
WebSocket Client untuk menghubungkan Godot ke Python Webcam Server
Berdasarkan protokol yang didefinisikan di WEBSOCKET_PROTOCOL.md
"""

signal connected()
signal disconnected()
signal frame_received(texture: ImageTexture)
signal metadata_received(metadata: Dictionary)
signal connection_error(error: String)

# WebSocket connection
var websocket_client: WebSocketPeer
var is_client_connected: bool = false
var is_connecting: bool = false

# Server configuration
var server_url: String = "ws://localhost:8765"
var reconnect_attempts: int = 0
var max_reconnect_attempts: int = 5
var reconnect_delay: float = 3.0

# Stream metadata
var stream_metadata: Dictionary = {}
var frame_count: int = 0
var last_frame_time: float = 0.0
var fps_counter: Array = []

# Debug options
var enable_logging: bool = true
var log_frames: bool = false

func _ready():
	_log("WebcamClient initialized")

func _process(_delta):
	if not websocket_client:
		return
	
	# Poll WebSocket untuk update state
	websocket_client.poll()
	
	var state = websocket_client.get_ready_state()
	
	match state:
		WebSocketPeer.STATE_CONNECTING:
			if not is_connecting:
				is_connecting = true
				_log("Connecting to server...")
		
		WebSocketPeer.STATE_OPEN:
			if not is_client_connected:
				_on_connected()
			_handle_incoming_packets()
		
		WebSocketPeer.STATE_CLOSING:
			_log("Connection closing...")
		
		WebSocketPeer.STATE_CLOSED:
			if is_client_connected:
				_on_disconnected()

func connect_to_server(url: String = "") -> bool:
	"""
	Menghubungkan ke webcam server
	"""
	if is_client_connected or is_connecting:
		_log("Already connected or connecting", "warning")
		return false
	
	if url != "":
		server_url = url
	
	_log("Attempting to connect to: " + server_url)
	
	# Create WebSocket peer
	websocket_client = WebSocketPeer.new()
	
	# Attempt connection
	var error = websocket_client.connect_to_url(server_url)
	
	if error != OK:
		_log("Failed to initiate connection: " + str(error), "error")
		connection_error.emit("Failed to connect: " + str(error))
		return false
	
	is_connecting = true
	return true

func disconnect_from_server():
	"""
	Memutuskan koneksi dari server
	"""
	if websocket_client:
		if is_client_connected:
			_log("Disconnecting from server...")
		websocket_client.close()
		websocket_client = null
	
	_reset_connection_state()

func send_config_message(config: Dictionary):
	"""
	Mengirim konfigurasi ke server (jika diperlukan)
	"""
	if not is_client_connected:
		_log("Not connected to server", "warning")
		return
	
	var message = {
		"type": "config",
		"data": config
	}
	
	var json_string = JSON.stringify(message)
	websocket_client.send_text(json_string)
	_log("Config sent: " + json_string)

func toggle_head_detection(enable: bool):
	"""
	Enable/disable head detection
	"""
	send_config_message({"head_detection": enable})

func set_cascade(cascade_type: String):
	"""
	Set cascade classifier (haar_biwi, lbp_biwi, opencv_default)
	"""
	send_config_message({"cascade_type": cascade_type})

func set_hat(hat_index: int):
	"""
	Set hat by index
	"""
	send_config_message({"hat_index": hat_index})

func next_hat():
	"""
	Switch to next hat
	"""
	send_config_message({"next_hat": true})

func previous_hat():
	"""
	Switch to previous hat
	"""
	send_config_message({"previous_hat": true})

func _handle_incoming_packets():
	"""
	Memproses paket yang masuk dari server
	"""
	while websocket_client.get_available_packet_count() > 0:
		var packet = websocket_client.get_packet()
		
		if packet.is_empty():
			continue
		
		if enable_logging and log_frames:
			_log("Received packet: " + _debug_packet_info(packet))
		
		# Cek apakah packet adalah JPEG binary data
		if is_jpeg_data(packet):
			_handle_frame_packet(packet)
		else:
			# Coba parse sebagai text/JSON hanya jika tidak binary
			# Gunakan error handling untuk avoid UTF-8 errors
			var packet_string = ""
			
			# Safe UTF-8 conversion
			var valid_text = true
			
			for i in range(min(packet.size(), 1024)): # Check only first 1KB for text
				var byte_val = packet[i]
				if byte_val < 32 and byte_val != 9 and byte_val != 10 and byte_val != 13: # Non-printable chars except tab, LF, CR
					valid_text = false
					break
			
			if valid_text:
				packet_string = packet.get_string_from_utf8()
				if packet_string.length() > 0 and packet_string.begins_with("{"):
					_handle_metadata_packet(packet_string)
				else:
					_log("Received non-JSON text packet: " + packet_string.substr(0, 100), "warning")
			else:
				_log("Received unknown binary packet: " + _debug_packet_info(packet), "warning")

func _handle_metadata_packet(json_string: String):
	"""
	Memproses metadata JSON dari server
	"""
	# Validasi JSON string
	if json_string.is_empty() or not json_string.begins_with("{"):
		_log("Invalid JSON string: " + json_string.substr(0, 50) + "...", "error")
		return
	
	var json = JSON.new()
	var parse_result = json.parse(json_string)
	
	if parse_result != OK:
		_log("Failed to parse metadata JSON: " + json_string, "error")
		return
	
	var metadata = json.data
	if typeof(metadata) != TYPE_DICTIONARY:
		_log("Metadata is not a dictionary: " + str(metadata), "error")
		return
	
	stream_metadata = metadata
	
	_log("Metadata received: " + str(metadata))
	metadata_received.emit(metadata)

func _handle_frame_packet(frame_data: PackedByteArray):
	"""
	Memproses frame JPEG dari server
	"""
	if frame_data.is_empty():
		_log("Received empty frame", "warning")
		return
	
	# Validasi JPEG header (harus dimulai dengan FF D8)
	if frame_data.size() < 2 or frame_data[0] != 0xFF or frame_data[1] != 0xD8:
		_log("Invalid JPEG header. Size: " + str(frame_data.size()) + ", First bytes: " + str(frame_data[0] if frame_data.size() > 0 else 0) + " " + str(frame_data[1] if frame_data.size() > 1 else 0), "error")
		return
	
	# Decode JPEG data ke Image
	var image = Image.new()
	var error = image.load_jpg_from_buffer(frame_data)
	
	if error != OK:
		_log("Failed to decode JPEG frame: " + str(error) + ", data size: " + str(frame_data.size()), "error")
		return
	
	# Convert Image ke ImageTexture
	var texture = ImageTexture.create_from_image(image)
	
	# Update frame statistics
	frame_count += 1
	_update_fps_counter()
	
	if log_frames:
		_log("Frame " + str(frame_count) + " received: " + str(frame_data.size()) + " bytes, resolution: " + str(image.get_width()) + "x" + str(image.get_height()))
	
	# Emit signal dengan texture yang siap digunakan
	frame_received.emit(texture)

func _update_fps_counter():
	"""
	Update FPS counter
	"""
	var current_time = Time.get_time_dict_from_system()
	var timestamp = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
	
	fps_counter.append(timestamp)
	
	# Keep only last 60 frames for FPS calculation
	if fps_counter.size() > 60:
		fps_counter.pop_front()

func get_current_fps() -> float:
	"""
	Menghitung FPS saat ini
	"""
	if fps_counter.size() < 2:
		return 0.0
	
	var time_diff = fps_counter[-1] - fps_counter[0]
	if time_diff <= 0:
		return 0.0
	
	return fps_counter.size() / time_diff

func _on_connected():
	"""
	Callback ketika koneksi berhasil
	"""
	is_client_connected = true
	is_connecting = false
	reconnect_attempts = 0
	
	_log("Connected to webcam server successfully!")
	connected.emit()

func _on_disconnected():
	"""
	Callback ketika koneksi terputus
	"""
	var was_connected = is_client_connected
	_reset_connection_state()
	
	_log("Disconnected from server")
	disconnected.emit()
	
	# Auto-reconnect jika koneksi terputus tak terduga
	if was_connected and reconnect_attempts < max_reconnect_attempts:
		_attempt_reconnect()

func _attempt_reconnect():
	"""
	Mencoba reconnect otomatis
	"""
	reconnect_attempts += 1
	_log("Attempting reconnect " + str(reconnect_attempts) + "/" + str(max_reconnect_attempts))
	
	# Wait before reconnecting
	await get_tree().create_timer(reconnect_delay).timeout
	
	if not is_client_connected:
		connect_to_server()

func _reset_connection_state():
	"""
	Reset state koneksi
	"""
	is_client_connected = false
	is_connecting = false
	frame_count = 0
	fps_counter.clear()
	stream_metadata.clear()

func get_connection_status() -> String:
	"""
	Mendapatkan status koneksi saat ini
	"""
	if is_client_connected:
		return "connected"
	elif is_connecting:
		return "connecting"
	else:
		return "disconnected"

func get_stream_info() -> Dictionary:
	"""
	Mendapatkan informasi stream
	"""
	return {
		"metadata": stream_metadata,
		"frame_count": frame_count,
		"fps": get_current_fps(),
		"status": get_connection_status()
	}

func _log(message: String, level: String = "info"):
	"""
	Logging utility
	"""
	if not enable_logging:
		return
	
	var timestamp = Time.get_datetime_string_from_system()
	var log_message = "[" + timestamp + "] [WebcamClient] [" + level.to_upper() + "] " + message
	
	match level:
		"error":
			push_error(log_message)
		"warning":
			push_warning(log_message)
		_:
			print(log_message)

func _debug_packet_info(packet: PackedByteArray) -> String:
	"""
	Debug utility untuk menampilkan info packet
	"""
	if packet.is_empty():
		return "Empty packet"
	
	var info = "Packet size: " + str(packet.size()) + ", "
	var first_bytes = "First bytes: "
	
	var max_bytes = min(packet.size(), 8)
	for i in range(max_bytes):
		first_bytes += "%02X " % packet[i]
	
	return info + first_bytes
	
func is_jpeg_data(data: PackedByteArray) -> bool:
	"""
	Check apakah data adalah valid JPEG
	"""
	if data.size() < 4:
		return false
	
	# JPEG signature: FF D8 (Start of Image)
	# JPEG end: FF D9 (End of Image)
	return data[0] == 0xFF and data[1] == 0xD8
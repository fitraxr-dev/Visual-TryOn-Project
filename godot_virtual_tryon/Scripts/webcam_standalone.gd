extends Control

# Main WebSocket Webcam Client - Standalone version
@onready var status_label = $HBoxContainer/Label  
@onready var texture_rect = $HBoxContainer/TextureRect

var websocket_client: WebSocketPeer
var is_connected_to_server = false

const SERVER_URL = "ws://localhost:8765"

func _ready():
	# Initialize WebSocket
	websocket_client = WebSocketPeer.new()
	status_label.text = "Initializing..."
	
	# Start connection
	_connect_to_server()

func _process(_delta):
	if websocket_client:
		websocket_client.poll()
		var state = websocket_client.get_ready_state()
		
		match state:
			WebSocketPeer.STATE_OPEN:
				if not is_connected_to_server:
					is_connected_to_server = true
					print("WebSocket connected!")
					status_label.text = "Connected"
					status_label.modulate = Color.GREEN
				
				# Handle incoming data
				while websocket_client.get_available_packet_count():
					_handle_packet()
			
			WebSocketPeer.STATE_CONNECTING:
				status_label.text = "Connecting..."
				status_label.modulate = Color.YELLOW
			
			WebSocketPeer.STATE_CLOSING:
				status_label.text = "Closing..."
				status_label.modulate = Color.ORANGE
			
			WebSocketPeer.STATE_CLOSED:
				var code = websocket_client.get_close_code()
				var reason = websocket_client.get_close_reason()
				print("WebSocket closed with code: ", code, " reason: ", reason)
				if is_connected_to_server:
					is_connected_to_server = false
					status_label.text = "Disconnected - Retrying..."
					status_label.modulate = Color.RED
					# Auto reconnect after 2 seconds
					await get_tree().create_timer(2.0).timeout
					_connect_to_server()
				elif code == -1:
					# Connection failed, retry
					status_label.text = "Connection Failed - Retrying..."
					status_label.modulate = Color.RED
					await get_tree().create_timer(3.0).timeout
					_connect_to_server()

func _connect_to_server():
	print("Attempting to connect to: ", SERVER_URL)
	status_label.text = "Connecting..."
	status_label.modulate = Color.YELLOW
	
	# Add headers for WebSocket connection
	var headers = PackedStringArray()
	headers.append("User-Agent: Godot WebSocket Client")
	
	var error = websocket_client.connect_to_url(SERVER_URL, headers)
	if error != OK:
		print("Failed to connect: ", error)
		status_label.text = "Connection Failed"
		status_label.modulate = Color.RED
	else:
		print("Connection attempt started...")

func _handle_packet():
	var packet = websocket_client.get_packet()
	
	# Try to decode as text first (JSON metadata)
	var text = packet.get_string_from_utf8()
	if text != "" and text.length() > 0:  # Check for valid text
		# It's likely a JSON message
		var json = JSON.new()
		var parse_result = json.parse(text)
		if parse_result == OK:
			var data = json.data
			print("Received metadata: ", data)
			return
	
	# If not JSON, treat as binary (JPEG frame)
	_process_jpeg_frame(packet)

func _process_jpeg_frame(data: PackedByteArray):
	if data.size() == 0:
		print("Received empty frame data")
		return
	
	# Create image from JPEG bytes
	var image = Image.new()
	var error = image.load_jpg_from_buffer(data)
	
	if error != OK:
		print("Failed to decode JPEG frame: ", error)
		return
	
	print("Successfully decoded frame: ", image.get_width(), "x", image.get_height())
	
	# Create texture from image
	var texture = ImageTexture.new()
	texture.set_image(image)
	
	# Update texture rect
	texture_rect.texture = texture

func _exit_tree():
	if websocket_client and is_connected_to_server:
		websocket_client.close()

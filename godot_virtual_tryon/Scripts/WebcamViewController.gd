extends Control

"""
Controller untuk WebcamView scene
Menampilkan video stream dari Python webcam server
"""

# Preload WebcamClient
const WebcamClient = preload("res://Scripts/WebcamClient.gd")

# UI Elements
@onready var video_display: TextureRect = $VBoxContainer/VideoContainer/VideoDisplay
@onready var status_label: Label = $VBoxContainer/StatusContainer/StatusLabel
@onready var connect_button: Button = $VBoxContainer/ControlsContainer/ConnectButton
@onready var disconnect_button: Button = $VBoxContainer/ControlsContainer/DisconnectButton
@onready var info_label: Label = $VBoxContainer/InfoContainer/InfoLabel

# WebSocket client
var webcam_client: WebcamClient

# Stream info
var frame_count: int = 0
var connection_time: float = 0.0

func _ready():
	# Initialize WebcamClient
	webcam_client = WebcamClient.new()
	add_child(webcam_client)
	
	# Connect signals
	webcam_client.connected.connect(_on_webcam_connected)
	webcam_client.disconnected.connect(_on_webcam_disconnected)
	webcam_client.frame_received.connect(_on_frame_received)
	webcam_client.metadata_received.connect(_on_metadata_received)
	webcam_client.connection_error.connect(_on_connection_error)
	
	# Connect UI signals
	connect_button.pressed.connect(_on_connect_pressed)
	disconnect_button.pressed.connect(_on_disconnect_pressed)
	
	# Initial UI state
	_update_ui_state("disconnected")
	
	# Setup video display
	video_display.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	video_display.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	video_display.size_flags_vertical = Control.SIZE_EXPAND_FILL

func _process(_delta):
	# Update connection time
	if webcam_client.is_client_connected:
		connection_time += _delta
	
	# Update info display
	_update_info_display()

func _on_connect_pressed():
	"""
	Handle connect button press
	"""
	status_label.text = "Connecting..."
	connect_button.disabled = true
	
	if not webcam_client.connect_to_server():
		status_label.text = "Failed to connect"
		connect_button.disabled = false

func _on_disconnect_pressed():
	"""
	Handle disconnect button press
	"""
	webcam_client.disconnect_from_server()

func _on_webcam_connected():
	"""
	Handle successful connection
	"""
	connection_time = 0.0
	frame_count = 0
	_update_ui_state("connected")
	status_label.text = "Connected to webcam server"

func _on_webcam_disconnected():
	"""
	Handle disconnection
	"""
	_update_ui_state("disconnected")
	status_label.text = "Disconnected from server"
	video_display.texture = null

func _on_frame_received(texture: ImageTexture):
	"""
	Handle new frame from server
	"""
	video_display.texture = texture
	frame_count += 1

func _on_metadata_received(metadata: Dictionary):
	"""
	Handle metadata from server
	"""
	print("Stream metadata: ", metadata)
	
	if metadata.has("width") and metadata.has("height"):
		var resolution = str(metadata.width) + "x" + str(metadata.height)
		status_label.text = "Connected - Resolution: " + resolution

func _on_connection_error(error: String):
	"""
	Handle connection error
	"""
	status_label.text = "Connection error: " + error
	_update_ui_state("disconnected")

func _update_ui_state(state: String):
	"""
	Update UI based on connection state
	"""
	match state:
		"connected":
			connect_button.disabled = true
			disconnect_button.disabled = false
			disconnect_button.visible = true
		"disconnected":
			connect_button.disabled = false
			disconnect_button.disabled = true
			disconnect_button.visible = false
		"connecting":
			connect_button.disabled = true
			disconnect_button.disabled = true

func _update_info_display():
	"""
	Update information display
	"""
	var info_text = ""
	
	if webcam_client.is_client_connected:
		var stream_info = webcam_client.get_stream_info()
		
		info_text += "Status: Connected\n"
		info_text += "Frames: " + str(frame_count) + "\n"
		info_text += "FPS: " + str("%.1f" % stream_info.fps) + "\n"
		info_text += "Connection Time: " + str("%.1f" % connection_time) + "s\n"
		
		if stream_info.metadata.has("width") and stream_info.metadata.has("height"):
			info_text += "Resolution: " + str(stream_info.metadata.width) + "x" + str(stream_info.metadata.height) + "\n"
	else:
		info_text = "Status: " + webcam_client.get_connection_status().capitalize()
	
	info_label.text = info_text

func _exit_tree():
	"""
	Cleanup when scene is destroyed
	"""
	if webcam_client:
		webcam_client.disconnect_from_server()
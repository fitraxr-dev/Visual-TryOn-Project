extends Control

"""
Controller untuk WebcamView scene
Menampilkan video stream dari Python webcam server dengan fitur head detection
"""

# UI Elements
@onready var video_display: TextureRect = $VBoxContainer/VideoContainer/VideoDisplay
@onready var status_label: Label = $VBoxContainer/StatusContainer/StatusLabel
@onready var connect_button: Button = $VBoxContainer/ControlsContainer/ConnectButton
@onready var disconnect_button: Button = $VBoxContainer/ControlsContainer/DisconnectButton
@onready var info_label: Label = $VBoxContainer/InfoContainer/InfoLabel

# Head Detection Controls - DARI SCENE!
@onready var head_detection_toggle: CheckButton = $VBoxContainer/HeadDetectionContainer/HeadDetectionToggle
@onready var cascade_options: OptionButton = $VBoxContainer/HeadDetectionContainer/CascadeContainer/CascadeOptions
@onready var hat_prev_button: Button = $VBoxContainer/HeadDetectionContainer/HatContainer/HatPrevButton
@onready var hat_next_button: Button = $VBoxContainer/HeadDetectionContainer/HatContainer/HatNextButton
@onready var hat_info_label: Label = $VBoxContainer/HeadDetectionContainer/HatContainer/HatLabel

# WebSocket client
var webcam_client: WebcamClient

# Stream info
var frame_count: int = 0
var connection_time: float = 0.0

# Head detection state
var head_detection_enabled: bool = true  # TRUE by default!
var current_cascade: String = "haar_biwi"
var current_hat_index: int = 0

func _ready():
	# Initialize WebcamClient
	webcam_client = WebcamClient.new()
	add_child(webcam_client)
	
	# Connect WebcamClient signals
	webcam_client.connected.connect(_on_webcam_connected)
	webcam_client.disconnected.connect(_on_webcam_disconnected)
	webcam_client.frame_received.connect(_on_frame_received)
	webcam_client.metadata_received.connect(_on_metadata_received)
	webcam_client.connection_error.connect(_on_connection_error)
	
	# Connect UI button signals
	connect_button.pressed.connect(_on_connect_pressed)
	disconnect_button.pressed.connect(_on_disconnect_pressed)
	
	# Connect Head Detection control signals
	head_detection_toggle.toggled.connect(_on_head_detection_toggled)
	cascade_options.item_selected.connect(_on_cascade_selected)
	hat_prev_button.pressed.connect(_on_previous_hat_pressed)
	hat_next_button.pressed.connect(_on_next_hat_pressed)
	
	# Initialize head detection UI state
	head_detection_toggle.button_pressed = head_detection_enabled
	cascade_options.select(0)  # Default to HAAR Biwi
	_update_hat_label()
	
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

func _on_head_detection_toggled(enabled: bool):
	"""
	Handle head detection toggle
	"""
	print("======================================")
	print("🔴 BUTTON CLICKED: Head Detection Toggle")
	print("🔴 New state:", "ENABLED" if enabled else "DISABLED")
	print("======================================")
	head_detection_enabled = enabled
	webcam_client.toggle_head_detection(enabled)

func _on_cascade_selected(index: int):
	"""
	Handle cascade selection
	"""
	var cascade_types = ["haar_biwi", "lbp_biwi", "opencv_default"]
	current_cascade = cascade_types[index]
	print("======================================")
	print("🔴 BUTTON CLICKED: Cascade Selection")
	print("🔴 Selected cascade:", current_cascade)
	print("======================================")
	webcam_client.set_cascade(current_cascade)

func _on_previous_hat_pressed():
	"""
	Handle previous hat button
	"""
	print("======================================")
	print("🔴 BUTTON CLICKED: Previous Hat")
	print("🔴 Current index:", current_hat_index)
	print("======================================")
	current_hat_index = max(0, current_hat_index - 1)
	webcam_client.previous_hat()
	_update_hat_label()

func _on_next_hat_pressed():
	"""
	Handle next hat button
	"""
	print("======================================")
	print("🔴 BUTTON CLICKED: Next Hat")
	print("🔴 Current index:", current_hat_index)
	print("======================================")
	current_hat_index += 1
	webcam_client.next_hat()
	_update_hat_label()

func _update_hat_label():
	"""
	Update hat display label
	"""
	hat_info_label.text = "Hat: %d" % (current_hat_index + 1)

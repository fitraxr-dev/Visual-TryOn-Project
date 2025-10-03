extends Node

"""
Simple test script untuk testing WebcamClient
Dapat dijalankan sebagai autoload atau attached ke node
"""

const WebcamClientScript = preload("res://Scripts/WebcamClient.gd")

var webcam_client: WebcamClient

func _ready():
	print("Testing WebcamClient connection...")
	
	# Create client
	webcam_client = WebcamClientScript.new()
	add_child(webcam_client)
	
	# Connect signals
	webcam_client.connected.connect(_on_connected)
	webcam_client.disconnected.connect(_on_disconnected)
	webcam_client.frame_received.connect(_on_frame_received)
	webcam_client.metadata_received.connect(_on_metadata_received)
	webcam_client.connection_error.connect(_on_error)
	
	# Try to connect
	var success = webcam_client.connect_to_server()
	if success:
		print("Connection initiated...")
	else:
		print("Failed to initiate connection")

func _on_connected():
	print("✓ Connected to webcam server!")

func _on_disconnected():
	print("✗ Disconnected from server")

func _on_frame_received(texture: ImageTexture):
	print("📹 Frame received: ", texture.get_width(), "x", texture.get_height())

func _on_metadata_received(metadata: Dictionary):
	print("📊 Metadata: ", metadata)

func _on_error(error: String):
	print("❌ Error: ", error)

func _input(event):
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_C:
				print("Connecting...")
				webcam_client.connect_to_server()
			KEY_D:
				print("Disconnecting...")
				webcam_client.disconnect_from_server()
			KEY_S:
				print("Status: ", webcam_client.get_connection_status())
				print("Stream Info: ", webcam_client.get_stream_info())
			KEY_ESCAPE:
				get_tree().quit()

func _exit_tree():
	if webcam_client:
		webcam_client.disconnect_from_server()
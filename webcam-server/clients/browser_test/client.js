/**
 * WebSocket Client untuk testing Webcam WebSocket Server
 */

class WebcamWebSocketClient {
  constructor() {
    this.websocket = null;
    this.isConnected = false;
    this.frameCount = 0;
    this.dataReceived = 0;
    this.connectionStartTime = null;
    this.lastFrameTime = null;
    this.fpsHistory = [];

    // Elements
    this.videoElement = document.getElementById("videoStream");
    this.placeholderElement = document.getElementById("placeholder");
    this.statusElement = document.getElementById("connectionStatus");
    this.connectBtn = document.getElementById("connectBtn");
    this.disconnectBtn = document.getElementById("disconnectBtn");
    this.logContainer = document.getElementById("logContainer");
    this.metadataContainer = document.getElementById("metadataContainer");
    this.configControls = document.getElementById("configControls");

    // Stats elements
    this.frameCountElement = document.getElementById("frameCount");
    this.dataReceivedElement = document.getElementById("dataReceived");
    this.currentFPSElement = document.getElementById("currentFPS");
    this.connectionTimeElement = document.getElementById("connectionTime");

    // Metadata elements
    this.resolutionElement = document.getElementById("resolution");
    this.fpsElement = document.getElementById("fps");
    this.streamTypeElement = document.getElementById("streamType");

    // Start stats update timer
    this.startStatsTimer();

    this.log("Client initialized", "info");
  }

  connect(url) {
    if (this.isConnected) {
      this.log("Already connected", "warning");
      return;
    }

    this.log(`Connecting to ${url}...`, "info");
    this.setStatus("connecting");

    try {
      this.websocket = new WebSocket(url);
      this.setupWebSocketHandlers();
    } catch (error) {
      this.log(`Connection error: ${error.message}`, "error");
      this.setStatus("disconnected");
    }
  }

  setupWebSocketHandlers() {
    this.websocket.onopen = (event) => {
      this.isConnected = true;
      this.connectionStartTime = Date.now();
      this.setStatus("connected");
      this.log("Connected to WebSocket server", "info");

      // Show metadata and config controls
      this.metadataContainer.style.display = "block";
      this.configControls.style.display = "block";

      // Update button states
      this.connectBtn.disabled = true;
      this.disconnectBtn.disabled = false;
    };

    this.websocket.onmessage = (event) => {
      if (typeof event.data === "string") {
        // JSON metadata message
        this.handleTextMessage(event.data);
      } else {
        // Binary frame data
        this.handleBinaryMessage(event.data);
      }
    };

    this.websocket.onclose = (event) => {
      this.isConnected = false;
      this.connectionStartTime = null;
      this.setStatus("disconnected");

      // Hide video and metadata
      this.hideVideo();
      this.metadataContainer.style.display = "none";
      this.configControls.style.display = "none";

      // Update button states
      this.connectBtn.disabled = false;
      this.disconnectBtn.disabled = true;

      if (event.wasClean) {
        this.log(`Connection closed cleanly (code: ${event.code})`, "info");
      } else {
        this.log(
          `Connection lost (code: ${event.code}, reason: ${event.reason})`,
          "warning"
        );
      }
    };

    this.websocket.onerror = (error) => {
      this.log(`WebSocket error: ${error}`, "error");
    };
  }

  handleTextMessage(data) {
    try {
      const message = JSON.parse(data);
      this.log(`Received metadata: ${JSON.stringify(message)}`, "info");

      if (message.type === "meta") {
        this.updateMetadata(message);
      }
    } catch (error) {
      this.log(`Error parsing JSON message: ${error.message}`, "error");
    }
  }

  handleBinaryMessage(data) {
    // Convert blob to object URL and display
    const blob = new Blob([data], { type: "image/jpeg" });
    const url = URL.createObjectURL(blob);

    // Update video element
    if (this.videoElement.src) {
      URL.revokeObjectURL(this.videoElement.src);
    }

    this.videoElement.src = url;
    this.showVideo();

    // Update stats
    this.frameCount++;
    this.dataReceived += data.size;

    // Calculate FPS
    const now = Date.now();
    if (this.lastFrameTime) {
      const timeDiff = now - this.lastFrameTime;
      const fps = 1000 / timeDiff;
      this.fpsHistory.push(fps);

      // Keep only last 30 frames for FPS calculation
      if (this.fpsHistory.length > 30) {
        this.fpsHistory.shift();
      }
    }
    this.lastFrameTime = now;

    // Log frame info occasionally
    if (this.frameCount % 100 === 0) {
      this.log(
        `Frame ${this.frameCount} received (${this.formatBytes(data.size)})`,
        "info"
      );
    }
  }

  updateMetadata(metadata) {
    this.resolutionElement.textContent = `${metadata.width}x${metadata.height}`;
    this.fpsElement.textContent = metadata.fps;
    this.streamTypeElement.textContent = metadata.type;
  }

  showVideo() {
    this.videoElement.style.display = "block";
    this.placeholderElement.style.display = "none";
  }

  hideVideo() {
    this.videoElement.style.display = "none";
    this.placeholderElement.style.display = "block";

    // Revoke object URL
    if (this.videoElement.src) {
      URL.revokeObjectURL(this.videoElement.src);
      this.videoElement.src = "";
    }
  }

  disconnect() {
    if (this.websocket && this.isConnected) {
      this.log("Disconnecting...", "info");
      this.websocket.close();
    }
  }

  sendConfig(config) {
    if (this.isConnected && this.websocket) {
      const message = JSON.stringify(config);
      this.websocket.send(message);
      this.log(`Sent config: ${message}`, "info");
    } else {
      this.log("Cannot send config: not connected", "warning");
    }
  }

  setStatus(status) {
    this.statusElement.className = `status ${status}`;

    switch (status) {
      case "connected":
        this.statusElement.textContent = "🟢 Connected";
        break;
      case "connecting":
        this.statusElement.textContent = "🟡 Connecting...";
        break;
      case "disconnected":
        this.statusElement.textContent = "🔴 Disconnected";
        break;
    }
  }

  log(message, level = "info") {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry ${level}`;
    logEntry.textContent = `[${timestamp}] [${level.toUpperCase()}] ${message}`;

    this.logContainer.appendChild(logEntry);
    this.logContainer.scrollTop = this.logContainer.scrollHeight;

    // Keep only last 100 log entries
    const entries = this.logContainer.querySelectorAll(".log-entry");
    if (entries.length > 100) {
      entries[0].remove();
    }
  }

  startStatsTimer() {
    setInterval(() => {
      this.updateStats();
    }, 1000);
  }

  updateStats() {
    // Update frame count
    this.frameCountElement.textContent = this.frameCount;

    // Update data received
    this.dataReceivedElement.textContent = this.formatBytes(this.dataReceived);

    // Update FPS
    if (this.fpsHistory.length > 0) {
      const avgFPS =
        this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length;
      this.currentFPSElement.textContent = avgFPS.toFixed(1);
    } else {
      this.currentFPSElement.textContent = "0";
    }

    // Update connection time
    if (this.connectionStartTime) {
      const connectionTime = Math.floor(
        (Date.now() - this.connectionStartTime) / 1000
      );
      this.connectionTimeElement.textContent = `${connectionTime}s`;
    } else {
      this.connectionTimeElement.textContent = "0s";
    }
  }

  formatBytes(bytes) {
    if (bytes === 0) return "0 B";

    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }
}

// Global client instance
let client = new WebcamWebSocketClient();

// Global functions for HTML buttons
function connectWebSocket() {
  const url = document.getElementById("serverUrl").value;
  client.connect(url);
}

function disconnectWebSocket() {
  client.disconnect();
}

function sendResolutionConfig() {
  const width = parseInt(document.getElementById("configWidth").value);
  const height = parseInt(document.getElementById("configHeight").value);

  if (width && height) {
    client.sendConfig({
      type: "config",
      resolution: [width, height],
    });
  } else {
    client.log("Invalid resolution values", "warning");
  }
}

function sendQualityConfig() {
  const quality = parseInt(document.getElementById("configQuality").value);

  if (quality >= 1 && quality <= 100) {
    client.sendConfig({
      type: "config",
      jpeg_quality: quality,
    });
  } else {
    client.log("JPEG quality must be between 1-100", "warning");
  }
}

// Handle page unload
window.addEventListener("beforeunload", () => {
  if (client.isConnected) {
    client.disconnect();
  }
});

// Handle keyboard shortcuts
document.addEventListener("keydown", (event) => {
  if (event.ctrlKey) {
    switch (event.key) {
      case "Enter":
        event.preventDefault();
        if (!client.isConnected) {
          connectWebSocket();
        }
        break;
      case "Escape":
        event.preventDefault();
        if (client.isConnected) {
          disconnectWebSocket();
        }
        break;
    }
  }
});

// Auto-connect on page load (optional)
// connectWebSocket();

/**
 * WebSocket connection manager for the AI chat assistant.
 * Handles connection lifecycle, message sending, and auto-reconnect.
 */

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws/chat';

console.log("MODE:", import.meta.env.MODE);
console.log("ENV:", import.meta.env);
console.log("WS_URL:", WS_URL);

class ChatWebSocket {
  constructor() {
    this.ws = null;
    this.listeners = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.isConnecting = false;
  }

  /**
   * Connect to the WebSocket server.
   * @param {Function} onMessage - Callback for received messages
   * @param {Function} onStatusChange - Callback for connection status changes
   */
  connect(onMessage, onStatusChange) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.maxReconnectAttempts = 5; // Reset reconnect ceiling on fresh connection

    try {
      this.ws = new WebSocket(WS_URL);
    } catch (err) {
      this.isConnecting = false;
      onStatusChange?.('error');
      return;
    }

    this.ws.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      onStatusChange?.('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.ws.onclose = () => {
      this.isConnecting = false;
      onStatusChange?.('disconnected');
      this._attemptReconnect();
    };

    this.ws.onerror = () => {
      this.isConnecting = false;
      onStatusChange?.('error');
    };
  }

  /**
   * Send a message with the current Redux form state.
   * @param {string} message - User's chat message
   * @param {Object} currentState - Current Redux interaction state
   */
  sendMessage(message, currentState) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return false;
    }

    this.ws.send(JSON.stringify({
      message,
      current_state: currentState,
    }));

    return true;
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect() {
    this.maxReconnectAttempts = 0; // Prevent auto-reconnect
    this.isConnecting = false;
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Attempt to reconnect with exponential backoff.
   */
  _attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.onStatusChange?.('failed');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);

    setTimeout(() => {
      this.onStatusChange?.('reconnecting');
      this.connect(this.onMessage, this.onStatusChange);
    }, delay);
  }
}

// Singleton instance
const chatApi = new ChatWebSocket();
export default chatApi;

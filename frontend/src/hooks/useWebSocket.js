/**
 * useWebSocket.js — Custom hook for real-time WebSocket communication.
 *
 * Features:
 * - Auto-reconnect with exponential backoff via ReconnectingWebSocket
 * - Clean teardown on unmount to prevent memory leaks
 * - Connection status tracking (CONNECTING, OPEN, CLOSED)
 * - JSON parsing of incoming messages
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';

const WS_URL = 'ws://localhost:8000/ws/stream';

const STATUS = {
  CONNECTING: 'CONNECTING',
  OPEN: 'OPEN',
  CLOSED: 'CLOSED',
};

export default function useWebSocket() {
  const [data, setData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState(STATUS.CONNECTING);
  const wsRef = useRef(null);

  useEffect(() => {
    // Create a ReconnectingWebSocket instance
    const ws = new ReconnectingWebSocket(WS_URL, [], {
      maxRetries: Infinity,
      reconnectionDelayGrowFactor: 1.5,
      maxReconnectionDelay: 10000,
      minReconnectionDelay: 1000,
    });

    wsRef.current = ws;

    ws.addEventListener('open', () => {
      setConnectionStatus(STATUS.OPEN);
    });

    ws.addEventListener('close', () => {
      setConnectionStatus(STATUS.CLOSED);
    });

    ws.addEventListener('error', () => {
      setConnectionStatus(STATUS.CLOSED);
    });

    ws.addEventListener('message', (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch {
        // Ignore non-JSON messages
      }
    });

    // Cleanup on unmount — prevents memory leaks
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  return { data, connectionStatus };
}

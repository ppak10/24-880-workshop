import { useEffect, useRef, useState } from "react";
import { fetchWeather, wsUrl, type WeatherData } from "@/lib/server";

const RECONNECT_DELAY = 3000;
const MAX_RETRIES = 10;

export function useWeather() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [connected, setConnected] = useState(false);
  const retriesRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Prime with REST on mount so the UI shows something immediately.
    fetchWeather().then(setWeather).catch(() => {});

    let destroyed = false;

    function connect() {
      if (destroyed) return;

      const ws = new WebSocket(wsUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retriesRef.current = 0;
      };

      ws.onmessage = (e: MessageEvent<string>) => {
        try {
          const msg = JSON.parse(e.data) as { type: string; data: WeatherData };
          if (msg.type === "weather") setWeather(msg.data);
        } catch {
          // ignore malformed frames
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (!destroyed && retriesRef.current < MAX_RETRIES) {
          retriesRef.current += 1;
          setTimeout(connect, RECONNECT_DELAY);
        }
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      destroyed = true;
      wsRef.current?.close();
    };
  }, []);

  return { weather, connected };
}

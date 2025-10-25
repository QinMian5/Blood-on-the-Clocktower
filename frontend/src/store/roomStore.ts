import { create } from "zustand";

import type { RoomCredentials, RoomSnapshot } from "../api/types";

function deriveStateFromSnapshot(snapshot: RoomSnapshot, state: RoomState) {
  const me = snapshot.players.find((player) => player.me);
  if (me && state.credentials) {
    return { snapshot, credentials: { ...state.credentials, seat: me.seat } };
  }
  return { snapshot };
}

// 使用 Zustand 管理房间实时状态，避免组件层层传递 props。
interface RoomState {
  snapshot: RoomSnapshot | null;
  status: "disconnected" | "connecting" | "connected";
  credentials: RoomCredentials | null;
  lastError: string | null;
  connect: (credentials: RoomCredentials) => void;
  disconnect: () => void;
  setSnapshot: (snapshot: RoomSnapshot) => void;
  setError: (message: string | null) => void;
}

let socket: WebSocket | null = null;

export const useRoomStore = create<RoomState>((set) => ({
  snapshot: null,
  status: "disconnected",
  credentials: null,
  lastError: null,
  connect: (credentials: RoomCredentials) => {
    if (socket) {
      socket.close();
      socket = null;
    }
    // 重新建立连接前重置状态，避免旧的房间信息残留。
    set({ status: "connecting", credentials, lastError: null });
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/rooms/${credentials.roomId}?token=${credentials.token}`;
    socket = new WebSocket(wsUrl);
    socket.addEventListener("open", () => {
      set({ status: "connected" });
    });
    socket.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data.toString());
        if (data.type === "snapshot" || data.type === "state_diff") {
          set((state) => deriveStateFromSnapshot(data.data as RoomSnapshot, state));
        } else if (data.type === "error") {
          set({ lastError: data.message ?? "Unknown error" });
        }
      } catch (error) {
        console.error("Invalid websocket message", error);
      }
    });
    socket.addEventListener("close", () => {
      set({ status: "disconnected" });
      socket = null;
    });
    socket.addEventListener("error", () => {
      set({ lastError: "Connection error" });
    });
  },
  disconnect: () => {
    if (socket) {
      socket.close();
      socket = null;
    }
    set({ status: "disconnected", credentials: null });
  },
  setSnapshot: (snapshot: RoomSnapshot) => set((state) => deriveStateFromSnapshot(snapshot, state)),
  setError: (message: string | null) => set({ lastError: message })
}));

export function updateSnapshot(snapshot: RoomSnapshot) {
  useRoomStore.getState().setSnapshot(snapshot);
}

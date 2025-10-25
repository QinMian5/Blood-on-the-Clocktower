import { apiClient, setAuthToken } from "./client";
import type { RoomSnapshot } from "./types";

export interface AssignmentAttachmentPayload {
  slot: string;
  index: number;
  role_id: string;
}

export interface SeatAssignmentPayload {
  role: string;
  attachments?: Array<AssignmentAttachmentPayload>;
}

export interface AssignRolesOptions {
  seed?: string;
  assignments?: Record<number, SeatAssignmentPayload>;
  finalize?: boolean;
}

export interface AssignRolesResponse {
  assignments: Record<string, { role_id: string; attachments: Array<AssignmentAttachmentPayload> }>;
  finalized: boolean;
}

export async function createRoom(options: { scriptId?: string; hostName?: string } = {}) {
  const payload: Record<string, unknown> = {};
  if (options.hostName) {
    payload.host_name = options.hostName;
  }
  if (options.scriptId) {
    payload.script_id = options.scriptId;
  }
  const response = await apiClient.post("/rooms", payload);
  const data = response.data as {
    room_id: string;
    join_code: string;
    room_code: string;
    host_token: string;
  };
  setAuthToken(data.host_token);
  return data;
}

export async function joinRoom(code: string, name?: string) {
  const payload: Record<string, unknown> = { code };
  if (name) {
    payload.name = name;
  }
  const response = await apiClient.post(`/rooms/join`, payload);
  const data = response.data as {
    room_id: string;
    player_id: string;
    seat: number;
    player_token: string;
  };
  setAuthToken(data.player_token);
  return data;
}

export async function updateSeat(roomId: string, seat: number, options: { playerId?: string } = {}) {
  const payload: Record<string, unknown> = { seat };
  if (options.playerId) {
    payload.player_id = options.playerId;
  }
  const response = await apiClient.post(`/rooms/${roomId}/seat`, payload);
  return response.data as { seat: number };
}

export async function fetchSnapshot(roomId: string) {
  const response = await apiClient.get(`/rooms/${roomId}/state`);
  return response.data as RoomSnapshot;
}

export async function assignRoles(roomId: string, options: AssignRolesOptions = {}) {
  const payload: Record<string, unknown> = {};
  if (options.seed) {
    payload.seed = options.seed;
  }
  if (options.assignments) {
    const normalized: Record<string, SeatAssignmentPayload> = {};
    for (const [seat, value] of Object.entries(options.assignments)) {
      normalized[seat] = {
        role: value.role,
        attachments: value.attachments?.map((attachment) => ({ ...attachment })) ?? []
      };
    }
    payload.assignments = normalized;
  }
  if (options.finalize) {
    payload.finalize = true;
  }
  const response = await apiClient.post(`/rooms/${roomId}/assign`, payload);
  return response.data as AssignRolesResponse;
}

export async function changePhase(roomId: string, phase: string) {
  const response = await apiClient.post(`/rooms/${roomId}/phase`, {
    to: phase
  });
  return response.data as { phase: string };
}

export async function resetRoom(roomId: string) {
  const response = await apiClient.post(`/rooms/${roomId}/reset`, {});
  return response.data as { status: string };
}

export async function setGameResult(roomId: string, result: string | null) {
  const response = await apiClient.post(`/rooms/${roomId}/result`, {
    result
  });
  return response.data as { result: string | null };
}

export async function nominate(roomId: string, nomineeSeat: number, nominatorSeat: number) {
  const response = await apiClient.post(`/rooms/${roomId}/nominate`, {
    nominee_seat: nomineeSeat,
    nominator_seat: nominatorSeat
  });
  return response.data as { id: string };
}

export async function startVote(roomId: string, nominationId: string) {
  const response = await apiClient.post(`/rooms/${roomId}/nominations/${nominationId}/start`, {});
  return response.data as { nomination_id: string };
}

export async function revertNomination(roomId: string, nominationId: string) {
  const response = await apiClient.post(`/rooms/${roomId}/nominations/${nominationId}/revert`, {});
  return response.data as { status: string };
}

export async function updateNominationTotal(roomId: string, nominationId: string, total: number | null) {
  const response = await apiClient.post(`/rooms/${roomId}/nominations/${nominationId}/total`, {
    total
  });
  return response.data as { status: string };
}

export async function sendVote(
  roomId: string,
  nominationId: string,
  value: boolean,
  options: { playerId?: string } = {}
) {
  const payload: Record<string, unknown> = {
    nomination_id: nominationId,
    value
  };
  if (options.playerId) {
    payload.player_id = options.playerId;
  }
  const response = await apiClient.post(`/rooms/${roomId}/vote`, payload);
  return response.data as { id: string };
}

export async function updatePlayerStatus(
  roomId: string,
  playerId: string,
  status:
    | "alive"
    | "fake_dead_vote"
    | "fake_dead_no_vote"
    | "dead_vote"
    | "dead_no_vote"
) {
  const response = await apiClient.post(`/rooms/${roomId}/players/${playerId}/status`, {
    status
  });
  return response.data as { status: string };
}

export async function recordExecution(
  roomId: string,
  options: { nominationId?: string | null; executedSeat?: number | null }
) {
  const response = await apiClient.post(`/rooms/${roomId}/execution`, {
    nomination_id: options.nominationId ?? null,
    executed_seat: options.executedSeat ?? null
  });
  return response.data as { day: number; nomination_id: string | null; executed: number | null };
}

export async function sendNightAction(
  roomId: string,
  type: string,
  options: { target?: number; payload?: Record<string, unknown> }
) {
  const response = await apiClient.post(`/rooms/${roomId}/action`, {
    type,
    target: options.target,
    payload: options.payload ?? {}
  });
  return response.data as { id: string };
}

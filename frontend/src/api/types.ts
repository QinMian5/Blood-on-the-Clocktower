// 房间快照结构，来自后端 REST / WS。
export interface RoomSnapshot {
  room: {
    id: string;
    phase: string;
    day: number;
    night: number;
    script_id: string;
    join_code?: string;
    game_result?: string | null;
  };
  players: Array<RoomPlayer>;
  nominations: Array<RoomNomination>;
  script: ScriptSummary;
  pending_assignments?: Record<string, PendingAssignmentView>;
  pending_assignments_meta?: {
    team_counts: Record<string, number>;
  };
  vote_session?: VoteSessionView;
  executions?: Array<ExecutionRecordView>;
}

export interface LocalizedRoleName {
  id: string | null;
  name: string;
  name_localized?: Record<string, string>;
  team?: string;
  team_label?: string | null;
}

export interface RoomPlayer {
  id: string;
  seat: number;
  name: string;
  is_alive: boolean;
  me: boolean;
  is_host: boolean;
  ghost_vote_used: boolean;
  is_bot: boolean;
  life_status: string;
  visible_status: string;
  ghost_vote_available: boolean;
  seat_conflict?: boolean;
  // 后端会在主持人或本人视角下返回角色的中英文名称。
  role_secret?: LocalizedRoleName | null;
  role_attachments?: Array<RoleAttachmentView>;
  note?: string;
}

export interface RoomNomination {
  id: string;
  day: number;
  nominee: number;
  by: number;
  ts: string;
  confirmed: boolean;
  vote_started: boolean;
  vote_completed: boolean;
  votes: Array<{ voter: number; player_id: string; value: boolean }>;
  manual_total?: number | null;
}

export interface ScriptRoleInfo {
  id: string;
  name: string;
  name_localized?: Record<string, string>;
  team: string;
  team_label?: string | null;
  description?: string | null;
  attachment_slots?: Array<RoleAttachmentSlot>;
}

export interface ScriptSummary {
  id: string;
  name: string;
  version: string;
  team_counts: Record<string, number>;
  team_distribution: Record<number, Record<string, number>>;
  roles: Array<ScriptRoleInfo>;
  rules?: Record<string, unknown>;
}

export interface RoleAttachmentSlot {
  id: string;
  label?: string;
  count?: number;
  team_filter?: Array<string>;
  allow_duplicates?: boolean;
  owner_view?: string;
}

export interface RoleAttachmentView {
  slot: string;
  slot_label?: string | null;
  index: number;
  role_id: string;
  role?: LocalizedRoleName | null;
}

export interface PendingAssignmentView {
  role_id: string;
  role?: LocalizedRoleName | null;
  attachments: Array<RoleAttachmentView>;
}

export interface VoteOrderEntry {
  player_id: string;
  seat: number;
  name: string;
  value?: boolean;
  can_vote: boolean;
}

export interface VoteSessionView {
  nomination_id: string;
  current_player_id: string | null;
  finished: boolean;
  order: Array<VoteOrderEntry>;
}

export interface ExecutionRecordView {
  day: number;
  nominee: number | null;
  executed: number | null;
  votes_for: number;
  alive_count: number;
  nomination_id?: string | null;
  target_dead?: boolean | null;
  ts: string;
}

export interface RoomCredentials {
  roomId: string;
  token: string;
  seat?: number | null;
  playerId?: string | null;
}

export interface AdminProfile {
  username: string;
}

export interface AdminUser {
  id: number;
  username: string;
  nickname: string;
  can_create_room: boolean;
  created_at: string;
}

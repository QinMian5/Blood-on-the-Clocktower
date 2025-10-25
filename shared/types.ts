export interface SnapshotLogEntry {
  ts: string;
  kind: string;
  data: Record<string, unknown>;
}

// 后端与前端共享的快照类型定义，方便脚本生成工具复用。
export interface LocalizedRoleName {
  id: string | null;
  name: string;
  name_localized?: Record<string, string>;
  team?: string;
  team_label?: string | null;
}

export interface SnapshotPlayer {
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
  role_secret?: LocalizedRoleName | null;
  role_attachments?: RoleAttachmentView[];
  note?: string;
}

export interface ScriptRoleInfo {
  id: string;
  name: string;
  name_localized?: Record<string, string>;
  team: string;
  team_label?: string | null;
  description?: string | null;
  attachment_slots?: RoleAttachmentSlot[];
}

export interface ScriptSummary {
  id: string;
  name: string;
  version: string;
  team_counts: Record<string, number>;
  team_distribution: Record<number, Record<string, number>>;
  roles: ScriptRoleInfo[];
  rules?: Record<string, unknown>;
}

export interface RoleAttachmentSlot {
  id: string;
  label?: string;
  count?: number;
  team_filter?: string[];
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
  attachments: RoleAttachmentView[];
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
  order: VoteOrderEntry[];
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

export interface SnapshotPayload {
  room: {
    id: string;
    phase: string;
    day: number;
    night: number;
    script_id: string;
    join_code?: string;
    game_result?: string | null;
  };
  players: SnapshotPlayer[];
  nominations: Array<{
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
  }>;
  script: ScriptSummary;
  pending_assignments?: Record<string, PendingAssignmentView>;
  pending_assignments_meta?: {
    team_counts: Record<string, number>;
  };
  vote_session?: VoteSessionView;
  executions?: ExecutionRecordView[];
}

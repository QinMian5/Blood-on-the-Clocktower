import {isAxiosError} from "axios";
import {Fragment, useCallback, useEffect, useMemo, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";

import {
    assignRoles,
    changePhase,
    fetchSnapshot,
    nominate,
    recordExecution,
    resetRoom,
    sendVote,
    setGameResult,
    startVote,
    updateNominationTotal,
    updatePlayerStatus,
    updateSeat,
    revertNomination,
    updatePlayerNote
} from "../api/rooms";
import type {
    LocalizedRoleName,
    PendingAssignmentView,
    RoleAttachmentView,
    RoleAttachmentSlot,
    RoomNomination,
    RoomPlayer,
    ScriptRoleInfo
} from "../api/types";
import {useRoomStore} from "../store/roomStore";

const ROLE_TEAM_ORDER = ["townsfolk", "outsider", "minion", "demon"];
const TEAM_LABEL: Record<string, string> = {
    townsfolk: "镇民",
    outsider: "外来者",
    minion: "爪牙",
    demon: "恶魔",
    unknown: "其他"
};
const TEAM_CARD_CLASSES: Record<string, string> = {
    townsfolk: "border-sky-500/60 bg-sky-500/10",
    outsider: "border-sky-500/60 bg-sky-500/10",
    minion: "border-rose-500/60 bg-rose-500/10",
    demon: "border-rose-500/60 bg-rose-500/10"
};

const LIFE_STATUS_OPTIONS: Array<{ value: LifeStatusValue; label: string }> = [
    {value: "alive", label: "存活"},
    {value: "fake_dead_vote", label: "假死（有票）"},
    {value: "fake_dead_no_vote", label: "假死（无票）"},
    {value: "dead_vote", label: "死亡（有票）"},
    {value: "dead_no_vote", label: "死亡（无票）"}
];

type LifeStatusValue =
    | "alive"
    | "fake_dead_vote"
    | "fake_dead_no_vote"
    | "dead_vote"
    | "dead_no_vote";

function describePhase(phase: string, day: number, night: number) {
    switch (phase) {
        case "lobby":
            return "大厅";
        case "night":
            return `第${day}天夜晚`;
        case "day":
            return `第${day}天白天`;
        case "vote":
            return `第${day}天投票`;
        case "resolve":
            return `第${day}天处决`;
        case "day_end":
            return `第${day}天日终`;
        default:
            return phase;
    }
}

function getNextPhase(phase: string) {
    switch (phase) {
        case "lobby":
            return "night";
        case "night":
            return "day";
        case "day":
            return "vote";
        case "vote":
            return "resolve";
        case "resolve":
            return "night";
        case "day_end":
            return "night";
        default:
            return "night";
    }
}

function getPreviousPhase(phase: string) {
    switch (phase) {
        case "lobby":
            return "lobby";
        case "night":
            return "resolve";
        case "day":
            return "night";
        case "vote":
            return "day";
        case "resolve":
            return "vote";
        case "day_end":
            return "resolve";
        default:
            return "lobby";
    }
}

interface RoleAttachmentSelection {
    slot: string;
    index: number;
    roleId: string | null;
}

interface EditableAssignment {
    roleId: string;
    attachments: RoleAttachmentSelection[];
}

function renderRole(role?: LocalizedRoleName | null) {
    if (!role) {
        return "未知角色";
    }
    const zhName = role.name_localized?.zh_CN ?? role.name_localized?.zh_cn;
    const baseName = zhName ?? role.name;
    const teamLabel = role.team_label ?? (role.team ? renderTeam(role.team) : "");
    return teamLabel ? `${baseName}（${teamLabel}）` : baseName;
}

function renderTeam(team?: string) {
    if (!team) return "";
    return TEAM_LABEL[team] ?? team;
}

function computeExecutionThreshold(alivePlayers: number) {
    return Math.floor(alivePlayers / 2) + 1;
}

function formatSeatLabel(seat: number) {
    return seat === 0 ? "说书人" : `${seat} 号`;
}

function describePlayerStatus(player: RoomPlayer, hostView: boolean) {
    const statusKey = hostView ? player.life_status : player.visible_status;
    switch (statusKey) {
        case "fake_dead_vote":
            return "假死（有票）";
        case "fake_dead_no_vote":
            return "假死（无票）";
        case "dead_vote":
            return player.ghost_vote_available ? "死亡（有票）" : "死亡（无票）";
        case "dead_no_vote":
            return "死亡（无票）";
        default:
            return "存活";
    }
}

function renderGameResult(result?: string | null) {
    if (result === "blue") {
        return "蓝方胜利";
    }
    if (result === "red") {
        return "红方胜利";
    }
    if (result === "storyteller") {
        return "说书人胜利";
    }
    return "未结束";
}

export function RoomPage() {
    const {roomId} = useParams();
    const navigate = useNavigate();
    const connect = useRoomStore((state) => state.connect);
    const setSnapshot = useRoomStore((state) => state.setSnapshot);
    const snapshot = useRoomStore((state) => state.snapshot);
    const status = useRoomStore((state) => state.status);
    const credentials = useRoomStore((state) => state.credentials);
    const lastError = useRoomStore((state) => state.lastError);

    const [hostMessage, setHostMessage] = useState<string | null>(null);
    const [hostMessageType, setHostMessageType] = useState<"info" | "error" | null>(null);
    const [hostActionBusy, setHostActionBusy] = useState(false);
    const [showRoles, setShowRoles] = useState(false);
    const [editableAssignments, setEditableAssignments] = useState<Record<number, EditableAssignment>>({});
    const [assignmentSaving, setAssignmentSaving] = useState(false);
    const [seatUpdating, setSeatUpdating] = useState<Record<string, boolean>>({});
    const [seatMessage, setSeatMessage] = useState<string | null>(null);
    const [seatMessageType, setSeatMessageType] = useState<"info" | "error" | null>(null);
    const [showPlayerList, setShowPlayerList] = useState(true);
    const [showHistory, setShowHistory] = useState(true);
    const [manualTotalDrafts, setManualTotalDrafts] = useState<Record<string, string>>({});
    const [manualTotalSaving, setManualTotalSaving] = useState<Record<string, boolean>>({});
    const [resetDialogOpen, setResetDialogOpen] = useState(false);
    const [gameEndDialogOpen, setGameEndDialogOpen] = useState(false);
    const [statusUpdating, setStatusUpdating] = useState<Record<string, boolean>>({});
    const [playerNoteDrafts, setPlayerNoteDrafts] = useState<Record<string, string>>({});
    const [playerNoteSaving, setPlayerNoteSaving] = useState<Record<string, boolean>>({});
    const [nomineeSeatInput, setNomineeSeatInput] = useState<string>("");
    const [nominatorSeatInput, setNominatorSeatInput] = useState<string>("");
    const [voteSubmitting, setVoteSubmitting] = useState(false);
    const [executionNominationId, setExecutionNominationId] = useState<string>("");
    const [executionSeat, setExecutionSeat] = useState<string>("");
    const [executionSubmitting, setExecutionSubmitting] = useState(false);
    const [executionSelectionTouched, setExecutionSelectionTouched] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("botc_token");
        if (roomId && token && status === "disconnected") {
            connect({roomId, token});
        }
    }, [connect, roomId, status]);

    useEffect(() => {
        if (!roomId) {
            return;
        }
        fetchSnapshot(roomId)
            .then((data) => {
                setSnapshot(data);
            })
            .catch((error: unknown) => {
                console.error("Failed to fetch snapshot", error);
                if (isAxiosError(error) && error.response?.status === 401) {
                    navigate("/");
                }
            });
    }, [roomId, navigate, setSnapshot]);

    const players: RoomPlayer[] = snapshot?.players ?? [];
    const me = players.find((player) => player.me);
    const activePlayers = players.filter((player) => player.seat > 0);
    const playerCount = activePlayers.length;
    const playersById = useMemo(() => {
        const map = new Map<string, RoomPlayer>();
        players.forEach((player) => map.set(player.id, player));
        return map;
    }, [players]);
    const seatOptions = useMemo(() => {
        const count = Math.max(players.filter((player) => !player.is_host).length, 1);
        return Array.from({length: count}, (_, index) => index + 1);
    }, [players]);
    const nominationSeatOptions = useMemo(() => {
        const seats = new Set<number>();
        seats.add(0);
        seatOptions.forEach((seat) => seats.add(seat));
        return Array.from(seats).sort((a, b) => a - b);
    }, [seatOptions]);
    const pendingAssignmentsRaw = snapshot?.pending_assignments ?? {};
    const pendingAssignments = useMemo(() => {
        const map = new Map<number, PendingAssignmentView>();
        Object.entries(pendingAssignmentsRaw).forEach(([seatKey, assignment]) => {
            const seat = Number(seatKey);
            map.set(seat, assignment);
        });
        return map;
    }, [pendingAssignmentsRaw]);
    const seatColumnPlayers = useMemo(() => {
        const map = new Map<number, RoomPlayer[]>();
        nominationSeatOptions.forEach((seat) => {
            if (seat > 0) {
                map.set(seat, []);
            }
        });
        players.forEach((player) => {
            if (!player.is_host && player.seat > 0) {
                if (!map.has(player.seat)) {
                    map.set(player.seat, []);
                }
                map.get(player.seat)!.push(player);
            }
        });
        return map;
    }, [players, nominationSeatOptions]);
    const pendingTeamCountsLabel = useMemo(() => {
        const counts = snapshot?.pending_assignments_meta?.team_counts;
        if (!counts) {
            return null;
        }
        return ROLE_TEAM_ORDER.map((team) => counts[team] ?? 0).join("/");
    }, [snapshot?.pending_assignments_meta]);

    const isHost = useMemo(() => {
        if (!snapshot) return credentials?.seat === 0;
        if (me) {
            return me.is_host || me.seat === 0;
        }
        return credentials?.seat === 0;
    }, [snapshot, me, credentials]);

    const myRole = me?.role_secret;
    const myRoleId = myRole?.id ?? null;
    const myStatus = me ? describePlayerStatus(me, isHost) : "";
    const myAttachments = me?.role_attachments ?? [];

    const scriptInfo = snapshot?.script;
    const scriptRoles = scriptInfo?.roles ?? [];
    const roleSections = useMemo(() => {
        if (!scriptRoles.length) {
            return [] as Array<{ team: string; roles: ScriptRoleInfo[] }>;
        }
        const groups: Record<string, ScriptRoleInfo[]> = {};
        scriptRoles.forEach((role) => {
            const teamKey = role.team ?? "unknown";
            if (!groups[teamKey]) {
                groups[teamKey] = [];
            }
            groups[teamKey].push(role);
        });
        const sections: Array<{ team: string; roles: ScriptRoleInfo[] }> = [];
        ROLE_TEAM_ORDER.forEach((team) => {
            const roles = groups[team];
            if (roles?.length) {
                sections.push({team, roles});
            }
        });
        Object.keys(groups)
            .filter((team) => !ROLE_TEAM_ORDER.includes(team))
            .sort()
            .forEach((team) => {
                const roles = groups[team];
                if (roles?.length) {
                    sections.push({team, roles});
                }
            });
        return sections;
    }, [scriptRoles]);
    const rolesById = useMemo(() => {
        const map = new Map<string, ScriptRoleInfo>();
        scriptRoles.forEach((role) => map.set(role.id, role));
        return map;
    }, [scriptRoles]);

    useEffect(() => {
        const pending = snapshot?.pending_assignments;
        if (!pending) {
            setEditableAssignments({});
            return;
        }
        const nextAssignments: Record<number, EditableAssignment> = {};
        Object.entries(pending).forEach(([seatKey, assignment]) => {
            const seat = Number(seatKey);
            const roleId = assignment.role_id;
            const scriptRole = roleId ? rolesById.get(roleId) : undefined;
            const slots: Array<RoleAttachmentSlot> = scriptRole?.attachment_slots ?? [];
            const attachmentMap = new Map<string, string | null>();
            assignment.attachments.forEach((attachment) => {
                attachmentMap.set(`${attachment.slot}:${attachment.index}`, attachment.role_id ?? null);
            });
            const attachments: RoleAttachmentSelection[] = [];
            if (slots.length > 0) {
                slots.forEach((slot) => {
                    const count = typeof slot.count === "number" && slot.count > 0 ? slot.count : 1;
                    for (let index = 0; index < count; index += 1) {
                        const key = `${slot.id}:${index}`;
                        const stored = attachmentMap.get(key);
                        attachments.push({
                            slot: slot.id,
                            index,
                            roleId: stored !== undefined ? stored : null
                        });
                    }
                });
            } else {
                assignment.attachments.forEach((attachment) => {
                    attachments.push({
                        slot: attachment.slot,
                        index: attachment.index,
                        roleId: attachment.role_id ?? null
                    });
                });
            }
            nextAssignments[seat] = {
                roleId,
                attachments
            };
        });
        setEditableAssignments(nextAssignments);
    }, [rolesById, snapshot?.pending_assignments]);

    const currentPhase = snapshot?.room.phase ?? "lobby";
    const currentDay = snapshot?.room.day ?? 0;
    const currentNight = snapshot?.room.night ?? 0;
    const phaseLabel = describePhase(currentPhase, currentDay, currentNight);
    const nextPhase = getNextPhase(currentPhase);
    const previousPhase = getPreviousPhase(currentPhase);
    const canGoPrevious = previousPhase !== currentPhase;
    const gameResult = snapshot?.room.game_result ?? null;
    const gameResultLabel = renderGameResult(gameResult);
    const storytellerAvailable = Boolean(
        (scriptInfo?.rules?.storyteller_win_available as boolean | undefined) ?? false
    );

    const teamCounts = scriptInfo?.team_counts ?? {};
    const teamDistribution = scriptInfo?.team_distribution ?? {};
    const nominations: RoomNomination[] = snapshot?.nominations ?? [];
    const voteSession = snapshot?.vote_session ?? null;
    const executions = snapshot?.executions ?? [];
    const executionsByDay = useMemo(() => {
        const map = new Map<number, typeof executions[number]>();
        executions.forEach((record) => {
            map.set(record.day, record);
        });
        return map;
    }, [executions]);
    const nominationsByDay = useMemo(() => {
        const grouped = new Map<number, RoomNomination[]>();
        nominations.forEach((nomination) => {
            if (!grouped.has(nomination.day)) {
                grouped.set(nomination.day, []);
            }
            grouped.get(nomination.day)!.push(nomination);
        });
        return Array.from(grouped.entries())
            .sort((a, b) => a[0] - b[0])
            .map(([day, items]) => ({
                day,
                nominations: items
            }));
    }, [nominations]);
    const todaysNominations = useMemo(
        () => nominations.filter((nomination) => nomination.day === currentDay),
        [nominations, currentDay]
    );
    useEffect(() => {
        const next: Record<string, string> = {};
        nominations.forEach((nomination) => {
            const yesVotes = nomination.votes.filter((vote) => vote.value).length;
            const baseValue = nomination.manual_total ?? yesVotes;
            next[nomination.id] = String(baseValue);
        });
        setManualTotalDrafts(next);
    }, [nominations]);
    useEffect(() => {
        const drafts: Record<string, string> = {};
        players.forEach((player) => {
            drafts[player.id] = player.note ?? "";
        });
        setPlayerNoteDrafts(drafts);
    }, [players]);
    const selectedExecutionNomination = useMemo(
        () => todaysNominations.find((item) => item.id === executionNominationId) ?? null,
        [todaysNominations, executionNominationId]
    );
    const hasExecutionTarget = useMemo(() => {
        if (executionSeat === "") {
            return false;
        }
        const parsed = Number.parseInt(executionSeat, 10);
        return !Number.isNaN(parsed) && parsed >= 0;
    }, [executionSeat]);
    const aliveCount = useMemo(
        () => players.filter((player) => !player.is_host && player.life_status === "alive").length,
        [players]
    );
    const resolveNominationTotal = useCallback(
        (nomination: RoomNomination) =>
            nomination.manual_total ?? nomination.votes.filter((vote) => vote.value).length,
        []
    );
    const executionBlockByDay = useMemo(() => {
        const grouped = new Map<number, RoomNomination[]>();
        nominations.forEach((nomination) => {
            if (!grouped.has(nomination.day)) {
                grouped.set(nomination.day, []);
            }
            grouped.get(nomination.day)!.push(nomination);
        });
        const aliveCounts = new Map<number, number>();
        executions.forEach((record) => {
            if (!aliveCounts.has(record.day)) {
                aliveCounts.set(record.day, record.alive_count);
            }
        });
        if (currentDay > 0 && !aliveCounts.has(currentDay)) {
            aliveCounts.set(currentDay, aliveCount);
        }
        const result = new Map<
            number,
            { nominationId: string | null; tie: boolean; hasCompleted: boolean; threshold: number }
        >();
        grouped.forEach((items, day) => {
            const completed = items.filter((item) => item.vote_completed);
            const aliveForDay = aliveCounts.get(day) ?? aliveCount;
            const threshold = computeExecutionThreshold(aliveForDay);
            if (completed.length === 0) {
                result.set(day, { nominationId: null, tie: false, hasCompleted: false, threshold });
                return;
            }
            let bestNominationId: string | null = null;
            let bestTotal = Number.NEGATIVE_INFINITY;
            let tie = false;
            completed.forEach((item) => {
                const total = resolveNominationTotal(item);
                if (total < threshold) {
                    return;
                }
                if (bestNominationId === null || total > bestTotal) {
                    bestNominationId = item.id;
                    bestTotal = total;
                    tie = false;
                } else if (total === bestTotal) {
                    tie = true;
                }
            });
            if (bestNominationId === null) {
                result.set(day, { nominationId: null, tie: false, hasCompleted: true, threshold });
            } else if (tie) {
                result.set(day, { nominationId: null, tie: true, hasCompleted: true, threshold });
            } else {
                result.set(day, { nominationId: bestNominationId, tie: false, hasCompleted: true, threshold });
            }
        });
        return result;
    }, [
        nominations,
        resolveNominationTotal,
        executions,
        currentDay,
        aliveCount
    ]);
    const todaysExecutionThreshold = useMemo(() => {
        const info = executionBlockByDay.get(currentDay);
        if (info) {
            return info.threshold;
        }
        return computeExecutionThreshold(aliveCount);
    }, [executionBlockByDay, currentDay, aliveCount]);
    const activeNomination = useMemo(() => {
        if (!voteSession) {
            return null;
        }
        return nominations.find((item) => item.id === voteSession.nomination_id) ?? null;
    }, [voteSession, nominations]);
    const currentVoteEntry = useMemo(() => {
        if (!voteSession || !voteSession.current_player_id) {
            return null;
        }
        return (
            voteSession.order.find((entry) => entry.player_id === voteSession.current_player_id) ?? null
        );
    }, [voteSession]);
    const canCurrentPlayerVote = currentVoteEntry?.can_vote ?? false;


    const handleSeatChange = useCallback(
        async (player: RoomPlayer, value: string) => {
            if (!snapshot) {
                return;
            }
            const nextSeat = value === "" ? 0 : Number.parseInt(value, 10);
            if (Number.isNaN(nextSeat)) {
                return;
            }
            if (!isHost && snapshot.room.phase !== "lobby") {
                setSeatMessageType("error");
                setSeatMessage("仅可在大厅阶段调整座位。");
                return;
            }
            setSeatMessage(null);
            setSeatMessageType(null);
            setSeatUpdating((state) => ({...state, [player.id]: true}));
            try {
                await updateSeat(
                    snapshot.room.id,
                    nextSeat,
                    isHost && !player.me ? {playerId: player.id} : {}
                );
                setSeatMessageType("info");
                setSeatMessage(`已更新 ${player.name} 的座位。`);
            } catch (error) {
                console.error("update seat failed", error);
                setSeatMessageType("error");
                setSeatMessage("调整座位失败，请稍后重试。");
            } finally {
                setSeatUpdating((state) => {
                    const nextState = {...state};
                    delete nextState[player.id];
                    return nextState;
                });
            }
        },
        [snapshot, isHost]
    );

    const handleStatusChange = useCallback(
        async (player: RoomPlayer, value: LifeStatusValue) => {
            if (!snapshot) {
                return;
            }
            setStatusUpdating((state) => ({...state, [player.id]: true}));
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await updatePlayerStatus(snapshot.room.id, player.id, value);
                setHostMessageType("info");
                setHostMessage(`已更新 ${player.name} 的状态。`);
            } catch (error) {
                console.error("update status failed", error);
                setHostMessageType("error");
                setHostMessage("调整玩家状态失败，请稍后重试。");
            } finally {
                setStatusUpdating((state) => {
                    const next = {...state};
                    delete next[player.id];
                    return next;
                });
            }
        },
        [snapshot]
    );

    const handlePlayerNoteDraftChange = useCallback((playerId: string, value: string) => {
        setPlayerNoteDrafts((drafts) => ({...drafts, [playerId]: value}));
    }, []);

    const handlePlayerNoteCommit = useCallback(
        async (player: RoomPlayer) => {
            if (!snapshot) {
                return;
            }
            const draft = playerNoteDrafts[player.id] ?? "";
            const current = playersById.get(player.id)?.note ?? "";
            if (draft === current) {
                return;
            }
            setPlayerNoteSaving((state) => ({...state, [player.id]: true}));
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await updatePlayerNote(snapshot.room.id, player.id, draft);
                setHostMessageType("info");
                setHostMessage(`已更新 ${player.name} 的备注。`);
            } catch (error) {
                console.error("update note failed", error);
                setHostMessageType("error");
                setHostMessage("更新备注失败，请稍后重试。");
            } finally {
                setPlayerNoteSaving((state) => {
                    const next = {...state};
                    delete next[player.id];
                    return next;
                });
            }
        },
        [snapshot, playerNoteDrafts, playersById]
    );

    const handleNominationSubmit = useCallback(async () => {
        if (!snapshot) {
            return;
        }
        const nominee = Number.parseInt(nomineeSeatInput, 10);
        const nominator = Number.parseInt(nominatorSeatInput, 10);
        if (Number.isNaN(nominee) || nominee < 0 || Number.isNaN(nominator) || nominator < 0) {
            setHostMessageType("error");
            setHostMessage("请先选择有效的提名人与被提名者座位号。");
            return;
        }
        setHostActionBusy(true);
        setHostMessage(null);
        setHostMessageType(null);
        try {
            await nominate(snapshot.room.id, nominee, nominator);
            setHostMessageType("info");
            setHostMessage(`已记录 ${formatSeatLabel(nominator)} 提名 ${formatSeatLabel(nominee)}。`);
            setNomineeSeatInput("");
            setNominatorSeatInput("");
        } catch (error) {
            console.error("nominate failed", error);
            setHostMessageType("error");
            setHostMessage(
                isAxiosError(error) ? error.response?.data?.detail ?? "提名失败" : "提名失败"
            );
        } finally {
            setHostActionBusy(false);
        }
    }, [snapshot, nomineeSeatInput, nominatorSeatInput]);

    const handleStartVoteForNomination = useCallback(
        async (nominationId: string) => {
            if (!snapshot) return;
            setHostActionBusy(true);
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await startVote(snapshot.room.id, nominationId);
                setHostMessageType("info");
                setHostMessage("已开始投票。");
            } catch (error) {
                console.error("start vote failed", error);
                setHostMessageType("error");
                setHostMessage(
                    isAxiosError(error) ? error.response?.data?.detail ?? "无法开始投票" : "无法开始投票"
                );
            } finally {
                setHostActionBusy(false);
            }
        },
        [snapshot]
    );

    const handleRevertNomination = useCallback(
        async (nominationId: string) => {
            if (!snapshot) return;
            setHostActionBusy(true);
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await revertNomination(snapshot.room.id, nominationId);
                setHostMessageType("info");
                setHostMessage("已撤销提名。");
            } catch (error) {
                console.error("revert nomination failed", error);
                setHostMessageType("error");
                setHostMessage(
                    isAxiosError(error) ? error.response?.data?.detail ?? "撤销失败" : "撤销失败"
                );
            } finally {
                setHostActionBusy(false);
            }
        },
        [snapshot]
    );

    const handleManualTotalInputChange = useCallback((nominationId: string, value: string) => {
        setManualTotalDrafts((prev) => ({...prev, [nominationId]: value}));
    }, []);

    const handleManualTotalCommit = useCallback(
        async (nominationId: string) => {
            if (!snapshot) {
                return;
            }
            const target = nominations.find((item) => item.id === nominationId);
            if (!target) {
                return;
            }
            const yesVotes = target.votes.filter((vote) => vote.value).length;
            const raw = manualTotalDrafts[nominationId] ?? "";
            const trimmed = raw.trim();
            let total: number | null = null;
            if (trimmed.length === 0) {
                if (target.manual_total === null || target.manual_total === undefined) {
                    return;
                }
                total = null;
            } else {
                const parsed = Number(trimmed);
                if (!Number.isFinite(parsed) || !Number.isInteger(parsed)) {
                    setHostMessageType("error");
                    setHostMessage("请填写有效的总得票数整数。");
                    return;
                }
                if (target.manual_total !== null && target.manual_total !== undefined) {
                    if (parsed === target.manual_total) {
                        return;
                    }
                } else if (parsed === yesVotes) {
                    return;
                }
                total = parsed;
            }
            setManualTotalSaving((prev) => ({...prev, [nominationId]: true}));
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await updateNominationTotal(snapshot.room.id, nominationId, total);
                setHostMessageType("info");
                setHostMessage(total === null ? "已恢复系统统计总票数。" : "已更新总得票数。");
            } catch (error) {
                console.error("update nomination total failed", error);
                setHostMessageType("error");
                setHostMessage(
                    isAxiosError(error)
                        ? error.response?.data?.detail ?? "更新总得票数失败"
                        : "更新总得票数失败"
                );
            } finally {
                setManualTotalSaving((prev) => {
                    const next = {...prev};
                    delete next[nominationId];
                    return next;
                });
            }
        },
        [snapshot, nominations, manualTotalDrafts]
    );

    const handleVoteCast = useCallback(
        async (value: boolean) => {
            if (!snapshot || !voteSession || !voteSession.nomination_id) {
                return;
            }
            const targetPlayerId = voteSession.current_player_id;
            if (!targetPlayerId) {
                return;
            }
            setVoteSubmitting(true);
            setSeatMessage(null);
            setSeatMessageType(null);
            try {
                const override = isHost && (!me || me.id !== targetPlayerId) ? {playerId: targetPlayerId} : undefined;
                await sendVote(snapshot.room.id, voteSession.nomination_id, value, override);
            } catch (error) {
                console.error("vote failed", error);
                setSeatMessageType("error");
                setSeatMessage(
                    isAxiosError(error) ? error.response?.data?.detail ?? "投票失败" : "投票失败"
                );
            } finally {
                setVoteSubmitting(false);
            }
        },
        [snapshot, voteSession, isHost, me]
    );

    const handleExecutionSubmit = useCallback(
        async (options?: {targetDead?: boolean | null}) => {
            if (!snapshot) {
                return;
            }
            const executedSeatValue = executionSeat ? Number.parseInt(executionSeat, 10) : null;
            if (
                executionSeat &&
                (executedSeatValue === null || Number.isNaN(executedSeatValue) || executedSeatValue < 0)
            ) {
                setHostMessageType("error");
                setHostMessage("请选择有效的处决座位号。");
                return;
            }
            setExecutionSubmitting(true);
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await recordExecution(snapshot.room.id, {
                    nominationId: executionNominationId || null,
                    executedSeat: executedSeatValue,
                    targetDead: options?.targetDead
                });
                let extraMessage = "";
                if (options?.targetDead === true) {
                    extraMessage = "（目标标记为死亡）";
                } else if (options?.targetDead === false) {
                    extraMessage = "（目标标记为存活）";
                }
                setHostMessageType("info");
                setHostMessage(`处决结果已记录${extraMessage}。`);
            } catch (error) {
                console.error("execution record failed", error);
                setHostMessageType("error");
                setHostMessage(
                    isAxiosError(error) ? error.response?.data?.detail ?? "记录处决失败" : "记录处决失败"
                );
            } finally {
                setExecutionSubmitting(false);
            }
        },
        [snapshot, executionSeat, executionNominationId]
    );

    const roleUsage = useMemo(() => {
        const counts = new Map<string, number>();
        Object.values(editableAssignments).forEach((assignment) => {
            if (assignment.roleId) {
                counts.set(assignment.roleId, (counts.get(assignment.roleId) ?? 0) + 1);
            }
            assignment.attachments.forEach((attachment) => {
                if (attachment.roleId) {
                    counts.set(attachment.roleId, (counts.get(attachment.roleId) ?? 0) + 1);
                }
            });
        });
        return counts;
    }, [editableAssignments]);

    const resolveSlotLabel = useCallback(
        (roleId: string | null | undefined, slotId: string, fallback?: string | null) => {
            if (fallback) {
                return fallback;
            }
            if (!roleId) {
                return slotId;
            }
            const role = rolesById.get(roleId);
            if (!role) {
                return slotId;
            }
            const slot = (role.attachment_slots ?? []).find((definition) => definition.id === slotId);
            return slot?.label ?? slotId;
        },
        [rolesById]
    );

    const formatRoleOptionLabel = useCallback(
        (role: ScriptRoleInfo, usage: number) => {
            const label = renderRole({
                id: role.id,
                name: role.name,
                name_localized: role.name_localized,
                team: role.team,
                team_label: role.team_label
            });
            return usage > 0 ? `${label}（已在场上${usage}次）` : label;
        },
        []
    );

    const handleGenerateAssignments = useCallback(async () => {
        if (!roomId) return;
        setHostActionBusy(true);
        setHostMessage(null);
        setHostMessageType(null);
        try {
            await assignRoles(roomId);
            setHostMessage("已生成角色预分配。");
            setHostMessageType("info");
        } catch (error: unknown) {
            console.error("assign roles failed", error);
            if (isAxiosError(error)) {
                setHostMessage(error.response?.data?.detail ?? "分配失败");
            } else {
                setHostMessage("分配失败");
            }
            setHostMessageType("error");
        } finally {
            setHostActionBusy(false);
        }
    }, [roomId]);

    const buildAssignmentPayload = useCallback(
        (assignmentsMap: Record<number, EditableAssignment>) => {
            const payload: Record<number, {
                role: string;
                attachments: Array<{ slot: string; index: number; role_id: string }>
            }> = {};
            Object.entries(assignmentsMap).forEach(([seatKey, assignment]) => {
                if (!assignment.roleId) {
                    return;
                }
                payload[Number(seatKey)] = {
                    role: assignment.roleId,
                    attachments: assignment.attachments
                        .filter((attachment) => Boolean(attachment.roleId))
                        .map((attachment) => ({
                            slot: attachment.slot,
                            index: attachment.index,
                            role_id: attachment.roleId as string
                        }))
                };
            });
            return payload;
        },
        []
    );

    const persistAssignments = useCallback(
        async (
            assignmentsMap: Record<number, EditableAssignment>,
            options: { finalize?: boolean; silent?: boolean } = {}
        ) => {
            if (!roomId) return;
            const payload = buildAssignmentPayload(assignmentsMap);
            if (Object.keys(payload).length === 0) {
                if (options.finalize) {
                    setHostMessage("暂无可确认的预分配，请先生成角色。");
                    setHostMessageType("error");
                }
                return;
            }
            if (!options.silent) {
                setHostMessage(null);
                setHostMessageType(null);
            }
            setAssignmentSaving(true);
            try {
                await assignRoles(roomId, {
                    assignments: payload,
                    finalize: options.finalize === true ? true : undefined
                });
                if (options.finalize) {
                    setHostMessage("角色分配已确认并下发。");
                    setHostMessageType("info");
                } else if (!options.silent) {
                    setHostMessage("预分配已保存。");
                    setHostMessageType("info");
                }
            } catch (error: unknown) {
                console.error("persist assignments failed", error);
                if (isAxiosError(error)) {
                    setHostMessage(error.response?.data?.detail ?? "保存失败");
                } else {
                    setHostMessage("保存失败");
                }
                setHostMessageType("error");
                if (roomId) {
                    fetchSnapshot(roomId)
                        .then((data) => setSnapshot(data))
                        .catch((refreshError) => {
                            console.error("failed to refresh snapshot", refreshError);
                        });
                }
            } finally {
                setAssignmentSaving(false);
            }
        },
        [roomId, buildAssignmentPayload, setSnapshot, setHostMessage, setHostMessageType]
    );

    const handleRoleSelection = useCallback(
        async (seat: number, roleId: string) => {
            if (!roomId) return;
            if (!roleId) {
                const nextAssignments = {...editableAssignments};
                delete nextAssignments[seat];
                setEditableAssignments(nextAssignments);
                await persistAssignments(nextAssignments, {silent: true});
                return;
            }
            const scriptRole = rolesById.get(roleId);
            const slots: Array<RoleAttachmentSlot> = scriptRole?.attachment_slots ?? [];
            const existing = editableAssignments[seat]?.attachments ?? [];
            const nextAttachments: RoleAttachmentSelection[] = [];
            slots.forEach((slot) => {
                const count = typeof slot.count === "number" && slot.count > 0 ? slot.count : 1;
                for (let index = 0; index < count; index += 1) {
                    const previous = existing.find(
                        (attachment) => attachment.slot === slot.id && attachment.index === index
                    );
                    nextAttachments.push({
                        slot: slot.id,
                        index,
                        roleId: previous ? previous.roleId : null
                    });
                }
            });
            const nextAssignments = {
                ...editableAssignments,
                [seat]: {
                    roleId,
                    attachments: nextAttachments
                }
            };
            setEditableAssignments(nextAssignments);
            await persistAssignments(nextAssignments, {silent: true});
        },
        [editableAssignments, persistAssignments, rolesById, roomId]
    );

    const handleAttachmentSelection = useCallback(
        async (seat: number, slotId: string, index: number, roleId: string) => {
            if (!roomId) return;
            const current = editableAssignments[seat];
            if (!current) {
                return;
            }
            const nextAssignments = {
                ...editableAssignments,
                [seat]: {
                    ...current,
                    attachments: current.attachments.map((attachment) =>
                        attachment.slot === slotId && attachment.index === index
                            ? {...attachment, roleId: roleId || null}
                            : attachment
                    )
                }
            };
            setEditableAssignments(nextAssignments);
            await persistAssignments(nextAssignments, {silent: true});
        },
        [editableAssignments, persistAssignments, roomId]
    );

    const handleFinalizeAssignments = useCallback(async () => {
        const issues: string[] = [];
        Object.entries(editableAssignments).forEach(([seatKey, assignment]) => {
            const seat = Number(seatKey);
            if (!assignment.roleId) {
                issues.push(`${seat} 号缺少主身份`);
                return;
            }
            const scriptRole = rolesById.get(assignment.roleId);
            if (!scriptRole) {
                issues.push(`${seat} 号角色无效`);
                return;
            }
            const slots: Array<RoleAttachmentSlot> = scriptRole.attachment_slots ?? [];
            slots.forEach((slot) => {
                const count = typeof slot.count === "number" && slot.count > 0 ? slot.count : 1;
                for (let index = 0; index < count; index += 1) {
                    const found = assignment.attachments.find(
                        (attachment) =>
                            attachment.slot === slot.id && attachment.index === index && attachment.roleId
                    );
                    if (!found) {
                        issues.push(`${seat} 号缺少 ${slot.label ?? slot.id}`);
                    }
                }
            });
        });
        if (issues.length > 0) {
            setHostMessage(`无法确认：${issues.join("，")}`);
            setHostMessageType("error");
            return;
        }
        await persistAssignments(editableAssignments, {finalize: true});
    }, [editableAssignments, persistAssignments, rolesById, setHostMessage, setHostMessageType]);

    const handlePhaseChange = async (phase: string) => {
        if (!roomId) return;
        setHostActionBusy(true);
        setHostMessage(null);
        setHostMessageType(null);
        try {
            await changePhase(roomId, phase);
            setHostMessage(`阶段已切换`);
            setHostMessageType("info");
        } catch (error: unknown) {
            console.error("phase change failed", error);
            if (isAxiosError(error)) {
                setHostMessage(error.response?.data?.detail ?? "阶段切换失败");
            } else {
                setHostMessage("阶段切换失败");
            }
            setHostMessageType("error");
        } finally {
            setHostActionBusy(false);
        }
    };

    const handleResetGame = useCallback(async () => {
        if (!roomId) return;
        setHostActionBusy(true);
        setHostMessage(null);
        setHostMessageType(null);
        try {
            await resetRoom(roomId);
            setHostMessage("房间已重置并回到大厅。");
            setHostMessageType("info");
        } catch (error: unknown) {
            console.error("reset room failed", error);
            if (isAxiosError(error)) {
                setHostMessage(error.response?.data?.detail ?? "重置失败");
            } else {
                setHostMessage("重置失败");
            }
            setHostMessageType("error");
        } finally {
            setHostActionBusy(false);
        }
    }, [roomId]);

    const handleResetConfirm = useCallback(() => {
        setResetDialogOpen(false);
        void handleResetGame();
    }, [handleResetGame]);

    const handleGameEnd = useCallback(
        async (result: string | null) => {
            if (!roomId) return;
            setHostActionBusy(true);
            setHostMessage(null);
            setHostMessageType(null);
            try {
                await setGameResult(roomId, result);
                if (result === null) {
                    setHostMessage("已清除游戏结果。");
                } else {
                    setHostMessage(`${renderGameResult(result)} 已记录。`);
                }
                setHostMessageType("info");
                setGameEndDialogOpen(false);
            } catch (error: unknown) {
                console.error("set result failed", error);
                if (isAxiosError(error)) {
                    setHostMessage(error.response?.data?.detail ?? "记录失败");
                } else {
                    setHostMessage("记录失败");
                }
                setHostMessageType("error");
            } finally {
                setHostActionBusy(false);
            }
        },
        [roomId]
    );

    if (!roomId) {
        return null;
    }

    const isMyTurn = Boolean(
        voteSession && voteSession.current_player_id && me && voteSession.current_player_id === me.id && canCurrentPlayerVote
    );
    const canHostAssist = Boolean(
        isHost && voteSession && voteSession.current_player_id && canCurrentPlayerVote
    );
    const canVoteNow = Boolean((isMyTurn || canHostAssist) && voteSession && !voteSession.finished);

    useEffect(() => {
        if (currentPhase !== "resolve") {
            if (executionNominationId) {
                setExecutionNominationId("");
            }
            if (executionSeat) {
                setExecutionSeat("");
            }
            if (executionSelectionTouched) {
                setExecutionSelectionTouched(false);
            }
            return;
        }
        if (!executionSelectionTouched && todaysNominations.length > 0) {
            if (!todaysNominations.some((item) => item.id === executionNominationId)) {
                const fallback = todaysNominations[todaysNominations.length - 1];
                setExecutionNominationId(fallback.id);
                setExecutionSeat(String(fallback.nominee));
            }
        }
    }, [
        currentPhase,
        todaysNominations,
        executionNominationId,
        executionSeat,
        executionSelectionTouched
    ]);

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100">
            <header className="border-b border-slate-700 bg-slate-800/80">
                <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-4">
                    <div>
                        <h1 className="text-2xl font-semibold">房间 {snapshot?.room.id ?? roomId}</h1>
                        <p className="text-sm text-slate-300">当前阶段：{phaseLabel}</p>
                        {isHost && snapshot?.room.join_code && (
                            <p className="text-sm text-slate-300">
                                加入码：<span className="font-mono text-emerald-300">{snapshot.room.join_code}</span>
                            </p>
                        )}
                    </div>
                    <div className="text-sm text-slate-300">
                        状态：{status}
                        {lastError && <span className="ml-2 text-rose-400">{lastError}</span>}
                    </div>
                </div>
            </header>

            <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-8">
                <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                        <h2 className="text-lg font-semibold">我的身份</h2>
                        <p className="mt-2 text-sm text-slate-300">{myRole ? renderRole(myRole) : "尚未分配角色"}</p>
                        {myStatus && <p className="text-xs text-slate-400">当前状态：{myStatus}</p>}
                        {myAttachments.length > 0 && (
                            <ul className="mt-3 space-y-1 text-xs text-slate-300">
                                {myAttachments.map((attachment) => (
                                    <li key={`me-${attachment.slot}-${attachment.index}`}>
                                        {resolveSlotLabel(myRoleId, attachment.slot, attachment.slot_label ?? undefined)}：
                                        {attachment.role ? renderRole(attachment.role) : "未选择"}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                        <h2 className="text-lg font-semibold">剧本阵营人数</h2>
                        <p className="mt-1 text-xs text-slate-400">当前 {playerCount} 人配置</p>
                        <ul className="mt-3 space-y-1 text-sm text-slate-300">
                            {Object.keys(teamCounts).length ? (
                                Object.entries(teamCounts).map(([team, count]) => (
                                    <li key={team}>
                                        {renderTeam(team)}：{count}
                                    </li>
                                ))
                            ) : (
                                <li>暂无阵营统计</li>
                            )}
                        </ul>
                        {Object.keys(teamDistribution).length > 0 && (
                            <details className="mt-3 text-xs text-slate-400">
                                <summary className="cursor-pointer text-slate-300">查看全部标准配置</summary>
                                <ul className="mt-2 space-y-1">
                                    {Object.entries(teamDistribution)
                                        .sort(([a], [b]) => Number(a) - Number(b))
                                        .map(([playersKey, counts]) => (
                                            <li key={playersKey}>
                                                {playersKey} 人：
                                                {Object.entries(counts)
                                                    .map(([team, count]) => `${renderTeam(team)} ${count}`)
                                                    .join(" · ")}
                                            </li>
                                        ))}
                                </ul>
                            </details>
                        )}
                    </div>

                    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5 md:col-span-2 lg:col-span-1">
                        <h2 className="text-lg font-semibold">房间信息</h2>
                        <ul className="mt-3 space-y-1 text-sm text-slate-300">
                            <li>剧本：{scriptInfo?.name ?? snapshot?.room.script_id}</li>
                            {isHost && snapshot?.room.join_code && (
                                <li>
                                    加入码：
                                    <span className="font-mono text-emerald-300">{snapshot.room.join_code}</span>
                                </li>
                            )}
                            <li>玩家人数：{playerCount}</li>
                        </ul>
                    </div>
                </section>

                {isHost && (
                    <section className="grid gap-6 lg:grid-cols-1">
                        <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                            <h2 className="text-lg font-semibold">阶段切换</h2>
                            <p className="mt-2 text-sm text-slate-300">当前阶段：{phaseLabel}</p>
                            <p className="text-xs text-slate-400">游戏结果：{gameResultLabel}</p>
                            <div className="mt-4 space-y-3">
                                <button
                                    type="button"
                                    className="w-full rounded border border-rose-500 px-3 py-2 text-sm font-semibold text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                    onClick={() => setResetDialogOpen(true)}
                                    disabled={hostActionBusy || assignmentSaving}
                                >
                                    重新开始
                                </button>
                                <div className="flex flex-wrap gap-2">
                                    <button
                                        type="button"
                                        className="flex-1 rounded border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:border-emerald-400 disabled:opacity-50"
                                        onClick={() => void handlePhaseChange(previousPhase)}
                                        disabled={hostActionBusy || assignmentSaving || !canGoPrevious}
                                    >
                                        返回上一阶段
                                    </button>
                                    <button
                                        type="button"
                                        className="flex-1 rounded border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:border-emerald-400 disabled:opacity-50"
                                        onClick={() => void handlePhaseChange(nextPhase)}
                                        disabled={hostActionBusy || assignmentSaving}
                                    >
                                        进入下一阶段
                                    </button>
                                </div>
                                <button
                                    type="button"
                                    className="w-full rounded border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:border-amber-400 disabled:opacity-50"
                                    onClick={() => setGameEndDialogOpen(true)}
                                    disabled={hostActionBusy || assignmentSaving}
                                >
                                    游戏结束
                                </button>
                            </div>
                        </div>

                    </section>
                )}

                {isHost && hostMessage && (
                    <div
                        className={`rounded-lg border px-4 py-2 text-sm ${
                            hostMessageType === "error"
                                ? "border-rose-500/60 bg-rose-500/10 text-rose-200"
                                : "border-emerald-500/60 bg-emerald-500/10 text-emerald-200"
                        }`}
                    >
                        {hostMessage}
                    </div>
                )}

                {isHost && currentPhase === "vote" && (
                    <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                        <h2 className="text-lg font-semibold">提名管理</h2>
                        <div className="mt-4 grid gap-3 md:grid-cols-3">
                            <label className="flex flex-col text-sm text-slate-300">
                                <span className="text-xs text-slate-400">提名者座位</span>
                                <select
                                    className="mt-1 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                    value={nominatorSeatInput}
                                    onChange={(event) => setNominatorSeatInput(event.target.value)}
                                    disabled={hostActionBusy}
                                >
                                    <option value="">选择座位</option>
                                    {nominationSeatOptions.map((seat) => (
                                        <option key={`nominator-${seat}`} value={seat}>
                                            {seat === 0 ? "0（说书人）" : seat}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <label className="flex flex-col text-sm text-slate-300">
                                <span className="text-xs text-slate-400">被提名者座位</span>
                                <select
                                    className="mt-1 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                    value={nomineeSeatInput}
                                    onChange={(event) => setNomineeSeatInput(event.target.value)}
                                    disabled={hostActionBusy}
                                >
                                    <option value="">选择座位</option>
                                    {nominationSeatOptions.map((seat) => (
                                        <option key={`nominee-${seat}`} value={seat}>
                                            {seat === 0 ? "0（说书人）" : seat}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <div className="flex items-end">
                                <button
                                    type="button"
                                    className="w-full rounded border border-rose-500 px-3 py-2 text-sm font-semibold text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                    onClick={() => void handleNominationSubmit()}
                                    disabled={hostActionBusy}
                                >
                                    确认提名
                                </button>
                            </div>
                        </div>
                        <div className="mt-6 space-y-3 text-sm text-slate-300">
                            {todaysNominations.length === 0 ? (
                                <p className="text-slate-400">今日尚无提名记录。</p>
                            ) : (
                                todaysNominations.map((nomination) => {
                                    const yesVotes = nomination.votes.filter((vote) => vote.value).length;
                                    const statusLabel = nomination.vote_completed
                                        ? "投票已完成"
                                        : nomination.vote_started
                                            ? "投票进行中"
                                            : "尚未开始投票";
                                    return (
                                        <div
                                            key={`manage-${nomination.id}`}
                                            className="rounded border border-slate-700/60 bg-slate-900/40 p-4"
                                        >
                                            <div
                                                className="flex flex-wrap items-center justify-between gap-2 text-slate-200">
                        <span>
                          {formatSeatLabel(nomination.by)} 提名 {formatSeatLabel(nomination.nominee)}
                        </span>
                                                <span className="text-xs text-slate-400">
                          {new Date(nomination.ts).toLocaleString()}
                        </span>
                                            </div>
                                            <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-400">
                                                <span>{statusLabel}</span>
                                                <span>赞成票：{yesVotes}</span>
                                                <span>记录票数：{nomination.votes.length}</span>
                                            </div>
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                {!nomination.vote_started && (
                                                    <button
                                                        type="button"
                                                        className="rounded border border-emerald-500 px-3 py-1 text-xs text-emerald-200 hover:bg-emerald-500/10 disabled:opacity-50"
                                                        onClick={() => void handleStartVoteForNomination(nomination.id)}
                                                        disabled={hostActionBusy}
                                                    >
                                                        开始投票
                                                    </button>
                                                )}
                                                <button
                                                    type="button"
                                                    className="rounded border border-rose-500 px-3 py-1 text-xs text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                                    onClick={() => void handleRevertNomination(nomination.id)}
                                                    disabled={hostActionBusy}
                                                >
                                                    撤销提名
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </section>
                )}

                {voteSession && (
                    <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                        <h2 className="text-lg font-semibold">当前投票</h2>
                        <p className="mt-2 text-sm text-slate-300">
                            {activeNomination
                                ? `${formatSeatLabel(activeNomination.by)} 提名 ${formatSeatLabel(activeNomination.nominee)}`
                                : "正在处理提名"}
                        </p>
                        <div className="mt-3 flex flex-wrap gap-2">
                            {voteSession.order.map((entry) => {
                                const isCurrent =
                                    !voteSession.finished && entry.player_id === voteSession.current_player_id;
                                const value = entry.value;
                                let classes = "flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold";
                                if (value === true) {
                                    classes += " bg-emerald-400 text-slate-900";
                                } else if (value === false) {
                                    classes += " bg-rose-500 text-slate-100";
                                } else {
                                    classes += " bg-slate-700 text-slate-200";
                                }
                                if (isCurrent) {
                                    classes += " ring-2 ring-amber-400";
                                }
                                return (
                                    <div key={entry.player_id}
                                         className="flex flex-col items-center gap-1 text-xs text-slate-300">
                                        <div className={classes}>{entry.seat}</div>
                                        {entry.value === true ? "赞成" : entry.value === false ? "反对" : "待投"}
                                    </div>
                                );
                            })}
                        </div>
                        <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-slate-300">
              <span>
                {voteSession.finished
                    ? "投票已结束"
                    : currentVoteEntry
                        ? `轮到 ${currentVoteEntry.seat} 号`
                        : "等待投票"}
              </span>
                            {!voteSession.finished && (
                                <div className="flex gap-2">
                                    <button
                                        type="button"
                                        className="rounded border border-emerald-500 px-3 py-1 text-sm text-emerald-200 hover:bg-emerald-500/10 disabled:opacity-50"
                                        onClick={() => void handleVoteCast(true)}
                                        disabled={!canVoteNow || voteSubmitting}
                                    >
                                        投票
                                    </button>
                                    <button
                                        type="button"
                                        className="rounded border border-rose-500 px-3 py-1 text-sm text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                        onClick={() => void handleVoteCast(false)}
                                        disabled={!canVoteNow || voteSubmitting}
                                    >
                                        不投票
                                    </button>
                                </div>
                            )}
                        </div>
                    </section>
                )}

                {isHost && currentPhase === "resolve" && (
                    <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                        <h2 className="text-lg font-semibold">处决记录</h2>
                        <p className="mt-2 text-sm text-slate-300">填写当日的处决结果，未处决请选择“无人处决”。</p>
                        <div className="mt-4 grid gap-3 md:grid-cols-3">
                            <label className="flex flex-col text-sm text-slate-300">
                                <span className="text-xs text-slate-400">对应提名</span>
                                <select
                                    className="mt-1 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                    value={executionNominationId}
                                    onChange={(event) => {
                                        const value = event.target.value;
                                        setExecutionSelectionTouched(true);
                                        setExecutionNominationId(value);
                                        if (!value) {
                                            setExecutionSeat("");
                                        } else {
                                            const match = todaysNominations.find((item) => item.id === value);
                                            setExecutionSeat(match ? String(match.nominee) : "");
                                        }
                                    }}
                                    disabled={executionSubmitting}
                                >
                                    <option value="">无提名 / 无处决</option>
                                    {todaysNominations.map((nomination) => (
                                        <option key={nomination.id} value={nomination.id}>
                                            {nomination.by} 号提名 {nomination.nominee} 号
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <label className="flex flex-col text-sm text-slate-300">
                                <span className="text-xs text-slate-400">被处决座位</span>
                                <select
                                    className="mt-1 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                    value={executionSeat}
                                    onChange={(event) => {
                                        setExecutionSelectionTouched(true);
                                        setExecutionSeat(event.target.value);
                                    }}
                                    disabled={executionSubmitting}
                                >
                                    <option value="">无人处决</option>
                                    {nominationSeatOptions.map((seat) => (
                                        <option key={`execution-seat-${seat}`} value={seat}>
                                            {seat === 0 ? "0（说书人）" : seat}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <div className="flex items-end">
                                <button
                                    type="button"
                                    className="w-full rounded border border-emerald-500 px-3 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-500/10 disabled:opacity-50"
                                    onClick={() => void handleExecutionSubmit()}
                                    disabled={executionSubmitting}
                                >
                                    记录处决
                                </button>
                            </div>
                            <div className="mt-3 space-y-2 text-xs text-slate-400">
                                <p>点击前请先修改玩家状态。</p>
                                <div className="flex flex-wrap gap-2 text-sm">
                                    <button
                                        type="button"
                                        className="rounded border border-rose-500 px-3 py-1 text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                        onClick={() => void handleExecutionSubmit({targetDead: true})}
                                        disabled={executionSubmitting || !hasExecutionTarget}
                                    >
                                        目标玩家死亡
                                    </button>
                                    <button
                                        type="button"
                                        className="rounded border border-sky-500 px-3 py-1 text-sky-200 hover:bg-sky-500/10 disabled:opacity-50"
                                        onClick={() => void handleExecutionSubmit({targetDead: false})}
                                        disabled={executionSubmitting || !hasExecutionTarget}
                                    >
                                        目标玩家未死亡
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div className="mt-4 space-y-3 text-xs text-slate-300">
                            <p>当前存活玩家数：{aliveCount}</p>
                            <p>处决门槛：{todaysExecutionThreshold}</p>
                            {selectedExecutionNomination ? (
                                <div className="rounded border border-slate-700/60 bg-slate-900/40 p-3">
                                    <p className="text-slate-200">
                                        {formatSeatLabel(selectedExecutionNomination.by)} 提名 {formatSeatLabel(selectedExecutionNomination.nominee)}
                                    </p>
                                    <p className="mt-1">赞成票：{selectedExecutionNomination.votes.filter((vote) => vote.value).length}</p>
                                    <ul className="mt-2 space-y-1">
                                        {selectedExecutionNomination.votes.length === 0 && <li>暂未记录投票。</li>}
                                        {selectedExecutionNomination.votes.map((vote, index) => {
                                            const voter = playersById.get(vote.player_id);
                                            return (
                                                <li key={`${selectedExecutionNomination.id}-detail-${index}`}>
                                                    {vote.voter} 号{voter ? `（${voter.name}）` : ""}：{vote.value ? "赞成" : "反对"}
                                                </li>
                                            );
                                        })}
                                    </ul>
                                </div>
                            ) : (
                                <p className="text-slate-400">请选择提名以查看详细投票信息。</p>
                            )}
                            {todaysNominations.length > 0 && (
                                <div className="rounded border border-slate-700/60 bg-slate-900/40 p-3">
                                    <h3 className="text-sm font-semibold text-slate-200">当日提名汇总</h3>
                                    <ul className="mt-2 space-y-1">
                                        {todaysNominations.map((nomination) => (
                                            <li key={`summary-${nomination.id}`}>
                                                {formatSeatLabel(nomination.by)} → {formatSeatLabel(nomination.nominee)} ·
                                                赞成票 {nomination.votes.filter((vote) => vote.value).length}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </section>
                )}

                <section className="rounded-xl border border-slate-700 bg-slate-800/60">
                    <div className="flex items-center justify-between border-b border-slate-700 px-5 py-3">
                        <h2 className="text-lg font-semibold">提名与投票记录</h2>
                        <button
                            type="button"
                            className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:border-emerald-400"
                            onClick={() => setShowHistory((value) => !value)}
                        >
                            {showHistory ? "折叠" : "展开"}
                        </button>
                    </div>
                    {showHistory ? (
                        nominationsByDay.length === 0 ? (
                            <p className="px-5 py-4 text-sm text-slate-300">尚无提名。</p>
                        ) : (
                            <div className="space-y-6 px-4 py-5 text-sm text-slate-300">
                                {nominationsByDay.map(({day, nominations: dayNominations}) => {
                                    const execution = executionsByDay.get(day);
                                    return (
                                        <div key={`day-${day}`} className="space-y-4">
                                            <div className="flex flex-wrap items-center justify-between gap-2">
                                                <h3 className="text-base font-semibold text-slate-200">第 {day} 日</h3>
                                                {execution && (
                                                    <span className="text-xs text-slate-400">
                            存活 {execution.alive_count}
                                                        {" · "}
                                                        {execution.executed !== null
                                                            ? execution.executed === 0
                                                                ? "处决说书人"
                                                                : `处决 ${execution.executed} 号`
                                                            : "无人处决"}
                          </span>
                                                )}
                                            </div>
                                            <div className="overflow-x-auto">
                                                <table className="min-w-full divide-y divide-slate-700 text-xs">
                                                    <thead className="bg-slate-900/40 text-slate-300">
                                                    <tr>
                                                        <th className="px-3 py-2 text-left">提名</th>
                                                        {seatOptions.map((seat) => {
                                                            const occupants = seatColumnPlayers.get(seat) ?? [];
                                                            return (
                                                                <th key={`day-${day}-seat-${seat}`}
                                                                    className="px-2 py-2 text-center">
                                                                    <div className="flex flex-col items-center gap-1">
                                                                        <span>{seat} 号</span>
                                                                        {occupants.length > 0 && (
                                                                            <span
                                                                                className="text-[10px] text-slate-400">
                                          {occupants.map((player) => player.name).join("、")}
                                        </span>
                                                                        )}
                                                                    </div>
                                                                </th>
                                                            );
                                                        })}
                                                        <th className="px-3 py-2 text-center">
                                                            {isHost ? "总票数" : "处决台"}
                                                        </th>
                                                    </tr>
                                                    </thead>
                                                    <tbody className="divide-y divide-slate-800 text-slate-200">
                                                    {dayNominations.map((nomination) => {
                                                        const yesVotes = nomination.votes.filter((vote) => vote.value).length;
                                                        const statusLabel = nomination.vote_completed
                                                            ? "投票已完成"
                                                            : nomination.vote_started
                                                                ? "投票进行中"
                                                                : "等待投票";
                                                        const draftValue = manualTotalDrafts[nomination.id] ?? String(nomination.manual_total ?? yesVotes);
                                                        const blockInfo = executionBlockByDay.get(day);
                                                        const isVoteCompleted = nomination.vote_completed;
                                                        let blockLabel = "";
                                                        let onBlock = false;
                                                        if (!isVoteCompleted) {
                                                            blockLabel = "投票未结束";
                                                        } else if (!blockInfo || !blockInfo.hasCompleted) {
                                                            blockLabel = "无人上处决台";
                                                        } else if (blockInfo.nominationId === null) {
                                                            blockLabel = blockInfo.tie
                                                                ? "票数相同，无人上处决台"
                                                                : "无人上处决台";
                                                        } else if (blockInfo.nominationId === nomination.id) {
                                                            blockLabel = "在处决台";
                                                            onBlock = true;
                                                        } else {
                                                            blockLabel = "未在处决台";
                                                        }
                                                        return (
                                                            <tr key={nomination.id}>
                                                                <td className="px-3 py-3 align-top">
                                                                    <div className="flex flex-col gap-1 text-slate-200">
                                      <span>
                                        {formatSeatLabel(nomination.by)} 提名 {formatSeatLabel(nomination.nominee)}
                                      </span>
                                                                        <span className="text-xs text-slate-400">
                                        {new Date(nomination.ts).toLocaleString()}
                                      </span>
                                                                        <span className="text-xs text-slate-400">
                                        {statusLabel} · 赞成 {yesVotes} · 记录 {nomination.votes.length}
                                      </span>
                                                                    </div>
                                                                </td>
                                                                {seatOptions.map((seat) => {
                                                                    const voteEntry = nomination.votes.find((vote) => vote.voter === seat);
                                                                    const voteValue = voteEntry ? voteEntry.value : undefined;
                                                                    const label = voteValue === true ? "赞成" : voteValue === false ? "反对" : "未投";
                                                                    const classes = voteValue === true
                                                                        ? "bg-emerald-500 text-slate-900"
                                                                        : "bg-rose-500 text-slate-100";
                                                                    return (
                                                                        <td
                                                                            key={`${nomination.id}-seat-${seat}`}
                                                                            className="px-2 py-2 text-center align-middle"
                                                                        >
                                        <span
                                            className={`inline-flex min-w-[3rem] items-center justify-center rounded px-2 py-1 text-xs font-semibold ${classes}`}
                                        >
                                          {label}
                                        </span>
                                                                        </td>
                                                                    );
                                                                })}
                                                                <td className="px-3 py-2 text-center align-middle text-slate-200">
                                                                    {isHost ? (
                                                                        <div className="flex flex-col items-center gap-1">
                                                                            <input
                                                                                type="number"
                                                                                className="w-20 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-center text-sm focus:outline-none focus:ring focus:ring-emerald-500"
                                                                                value={draftValue}
                                                                                onChange={(event) =>
                                                                                    handleManualTotalInputChange(nomination.id, event.target.value)
                                                                                }
                                                                                onBlur={() => void handleManualTotalCommit(nomination.id)}
                                                                                onKeyDown={(event) => {
                                                                                    if (event.key === "Enter") {
                                                                                        event.preventDefault();
                                                                                        void handleManualTotalCommit(nomination.id);
                                                                                    }
                                                                                }}
                                                                                disabled={manualTotalSaving[nomination.id]}
                                                                            />
                                                                            <span className={`text-[11px] ${
                                                                                onBlock ? "text-emerald-300" : "text-slate-400"
                                                                            }`}>
                                                                                {blockLabel}
                                                                            </span>
                                                                        </div>
                                                                    ) : (
                                                                        <span
                                                                            className={onBlock
                                                                                ? "font-semibold text-emerald-300"
                                                                                : "text-slate-200"}
                                                                        >
                                                                            {blockLabel}
                                                                        </span>
                                                                    )}
                                                                </td>
                                                            </tr>
                                                        );
                                                    })}
                                                    </tbody>
                                                </table>
                                            </div>
                                            {execution && (
                                                <div
                                                    className="rounded border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
                                                    处决结果：
                                                    {execution.executed !== null
                                                        ? execution.executed === 0
                                                            ? "说书人"
                                                            : `${execution.executed} 号`
                                                        : "无人处决"}
                                                    ，存活 {execution.alive_count}
                                                    {execution.target_dead !== undefined && execution.target_dead !== null && (
                                                        <>
                                                            {" · "}
                                                            {execution.target_dead ? "目标死亡" : "目标存活"}
                                                        </>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )
                    ) : (
                        <p className="px-5 py-4 text-sm text-slate-300">点击“展开”查看提名与投票详情。</p>
                    )}
                </section>


                <section className="rounded-xl border border-slate-700 bg-slate-800/60">
                    <div className="flex items-center justify-between border-b border-slate-700 px-5 py-3">
                        <h2 className="text-lg font-semibold">玩家列表</h2>
                        <button
                            type="button"
                            className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:border-emerald-400"
                            onClick={() => setShowPlayerList((value) => !value)}
                        >
                            {showPlayerList ? "折叠" : "展开"}
                        </button>
                    </div>
                    {showPlayerList ? (
                        <>
                            <div className="overflow-x-auto px-4 pb-4">
                                <table className="min-w-full divide-y divide-slate-700 text-sm">
                                    <thead className="bg-slate-800/80">
                                    <tr>
                                        <th className="px-4 py-2 text-left">座位</th>
                                        <th className="px-4 py-2 text-left">姓名</th>
                                        <th className="px-4 py-2 text-left">状态</th>
                                        {isHost && <th className="px-4 py-2 text-left">角色</th>}
                                        {isHost && <th className="px-4 py-2 text-left">备注</th>}
                                    </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-800">
                                    {players.map((player) => {
                                        const visibleRole = player.role_secret;
                                        const pending = pendingAssignments.get(player.seat);
                                        const roleSource = visibleRole ?? pending?.role ?? null;
                                        const attachments: RoleAttachmentView[] =
                                            (player.role_attachments && player.role_attachments.length > 0
                                                ? player.role_attachments
                                                : pending?.attachments) ?? [];
                                        const isPendingOnly = !visibleRole && Boolean(pending);
                                        const assignmentRoleId =
                                            editableAssignments[player.seat]?.roleId ??
                                            pending?.role_id ??
                                            (player.role_secret?.id ?? null);
                                        const statusLabel = describePlayerStatus(player, isHost);
                                        return (
                                            <tr key={player.id} className={player.me ? "bg-slate-800/70" : undefined}>
                                                <td className="px-4 py-2 font-mono">
                                                    {(() => {
                                                        const canHostEdit = isHost;
                                                        const canSelfEdit = player.me && !isHost && currentPhase === "lobby";
                                                        const selectValue = player.seat >= 0 ? String(player.seat) : "";
                                                        const hasConflict = Boolean(player.seat_conflict);
                                                        if (canHostEdit) {
                                                            return (
                                                                <div className="flex items-center gap-2">
                                                                    <select
                                                                        className="rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-emerald-500"
                                                                        value={selectValue}
                                                                        onChange={(event) => handleSeatChange(player, event.target.value)}
                                                                        disabled={seatUpdating[player.id]}
                                                                    >
                                                                        <option key="seat-0" value="0">0</option>
                                                                        {seatOptions.map((option) => (
                                                                            <option key={`seat-${option}`}
                                                                                    value={option}>
                                                                                {option}
                                                                            </option>
                                                                        ))}
                                                                    </select>
                                                                    {hasConflict &&
                                                                        <span className="text-amber-400">!</span>}
                                                                </div>
                                                            );
                                                        }
                                                        if (canSelfEdit) {
                                                            return (
                                                                <div className="flex items-center gap-2">
                                                                    <select
                                                                        className="rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-emerald-500"
                                                                        value={selectValue}
                                                                        onChange={(event) => handleSeatChange(player, event.target.value)}
                                                                        disabled={seatUpdating[player.id]}
                                                                    >
                                                                        {/*<option key="seat-0" value="0">0</option>*/}
                                                                        {seatOptions.map((option) => (
                                                                            <option key={`seat-${option}`}
                                                                                    value={option}>
                                                                                {option}
                                                                            </option>
                                                                        ))}
                                                                    </select>
                                                                    {hasConflict &&
                                                                        <span className="text-amber-400">!</span>}
                                                                </div>
                                                            );
                                                        }
                                                        return (
                                                            <span
                                                                className={hasConflict ? "text-amber-300" : undefined}>
                                  {player.seat >= 0 ? player.seat : "未选择"}
                                                                {hasConflict &&
                                                                    <span className="ml-1 font-bold">!</span>}
                                </span>
                                                        );
                                                    })()}
                                                </td>
                                                <td className="px-4 py-2">
                                                    {player.name}
                                                    {player.is_host && (
                                                        <span
                                                            className="ml-2 rounded bg-rose-500/20 px-2 text-xs text-rose-200">说书人</span>
                                                    )}
                                                    {player.me && (
                                                        <span
                                                            className="ml-2 rounded bg-emerald-500/20 px-2 text-xs text-emerald-200">你</span>
                                                    )}
                                                </td>
                                                <td className="px-4 py-2">
                                                    <div className="flex flex-col gap-2">
                                                        {!isHost && (
                                                            <span>{statusLabel}</span>
                                                        )}
                                                        {isHost && player.is_host && (
                                                            <span>{statusLabel}</span>
                                                        )}
                                                        {isHost && !player.is_host && (
                                                            <select
                                                                className="w-full rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                                                value={player.life_status}
                                                                onChange={(event) =>
                                                                    handleStatusChange(player, event.target.value as LifeStatusValue)
                                                                }
                                                                disabled={statusUpdating[player.id]}
                                                            >
                                                                {LIFE_STATUS_OPTIONS.map((option) => (
                                                                    <option key={`${player.id}-${option.value}`}
                                                                            value={option.value}>
                                                                        {option.label}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                        )}
                                                    </div>
                                                </td>
                                                  {isHost && (
                                                      <td className="px-4 py-2 align-top">
                                                          {player.is_host ? (
                                                              <div className="flex flex-wrap gap-2">
                                                                  {pendingTeamCountsLabel && (
                                                                      <p className="w-full text-xs text-slate-400">
                                                                          预分配阵营：{pendingTeamCountsLabel}
                                                                      </p>
                                                                  )}
                                                                <button
                                                                    type="button"
                                                                    className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:border-emerald-400 disabled:opacity-50"
                                                                    onClick={handleGenerateAssignments}
                                                                    disabled={hostActionBusy || assignmentSaving}
                                                                >
                                                                    生成预分配
                                                                </button>
                                                                <button
                                                                    type="button"
                                                                    className="rounded border border-rose-500 px-3 py-1 text-xs text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                                                    onClick={handleFinalizeAssignments}
                                                                    disabled={hostActionBusy || assignmentSaving}
                                                                >
                                                                    确认下发
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <div className="space-y-3">
                                                                <div>
                                                                    <label className="block text-xs text-slate-400"
                                                                           htmlFor={`role-select-${player.id}`}>
                                                                        预分配角色
                                                                    </label>
                                                                    <select
                                                                        id={`role-select-${player.id}`}
                                                                        className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                                                        value={editableAssignments[player.seat]?.roleId ?? ""}
                                                                        onChange={(event) => handleRoleSelection(player.seat, event.target.value)}
                                                                        disabled={assignmentSaving || hostActionBusy}
                                                                    >
                                                                        <option value="">未选择</option>
                                                                        {scriptRoles.map((role) => {
                                                                            const usage =
                                                                                (roleUsage.get(role.id) ?? 0) -
                                                                                ((editableAssignments[player.seat]?.roleId ?? "") === role.id ? 1 : 0);
                                                                            return (
                                                                                <option key={role.id} value={role.id}>
                                                                                    {formatRoleOptionLabel(role, usage)}
                                                                                </option>
                                                                            );
                                                                        })}
                                                                    </select>
                                                                    {isPendingOnly && (
                                                                        <span
                                                                            className="ml-2 rounded bg-amber-500/20 px-2 text-xs text-amber-200">预分配</span>
                                                                    )}
                                                                </div>
                                                                {(() => {
                                                                    const assignment = editableAssignments[player.seat];
                                                                    const selectedRoleId = assignment?.roleId ?? "";
                                                                    const scriptRole = selectedRoleId ? rolesById.get(selectedRoleId) : undefined;
                                                                    const slots: Array<RoleAttachmentSlot> = scriptRole?.attachment_slots ?? [];
                                                                    if (!selectedRoleId) {
                                                                        return <p
                                                                            className="text-xs text-slate-400">请选择角色以配置附加身份。</p>;
                                                                    }
                                                                    if (slots.length === 0) {
                                                                        return <p
                                                                            className="text-xs text-slate-400">无需附加角色</p>;
                                                                    }
                                                                    return (
                                                                        <div className="space-y-2">
                                                                            {slots.map((slot) => {
                                                                                const count =
                                                                                    typeof slot.count === "number" && slot.count > 0 ? slot.count : 1;
                                                                                const slotOptions = scriptRoles.filter((role) =>
                                                                                    !slot.team_filter || slot.team_filter.length === 0
                                                                                        ? true
                                                                                        : slot.team_filter.includes(role.team)
                                                                                );
                                                                                return (
                                                                                    <div
                                                                                        key={`${player.seat}-${slot.id}`}>
                                                                                        <span
                                                                                            className="block text-xs text-slate-400">{slot.label ?? slot.id}</span>
                                                                                        {Array.from({length: count}).map((_, index) => {
                                                                                            const currentAttachment = assignment.attachments.find(
                                                                                                (item) => item.slot === slot.id && item.index === index
                                                                                            );
                                                                                            const value = currentAttachment?.roleId ?? "";
                                                                                            return (
                                                                                                <select
                                                                                                    key={`${player.seat}-${slot.id}-${index}`}
                                                                                                    className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-rose-500"
                                                                                                    value={value}
                                                                                                    onChange={(event) =>
                                                                                                        handleAttachmentSelection(
                                                                                                            player.seat,
                                                                                                            slot.id,
                                                                                                            index,
                                                                                                            event.target.value
                                                                                                        )
                                                                                                    }
                                                                                                    disabled={assignmentSaving || hostActionBusy}
                                                                                                >
                                                                                                    <option
                                                                                                        value="">未选择
                                                                                                    </option>
                                                                                                    {slotOptions.map((role) => {
                                                                                                        const usage =
                                                                                                            (roleUsage.get(role.id) ?? 0) - (value === role.id ? 1 : 0);
                                                                                                        return (
                                                                                                            <option
                                                                                                                key={`${slot.id}-${role.id}-${index}`}
                                                                                                                value={role.id}>
                                                                                                                {formatRoleOptionLabel(role, usage)}
                                                                                                            </option>
                                                                                                        );
                                                                                                    })}
                                                                                                </select>
                                                                                            );
                                                                                        })}
                                                                                    </div>
                                                                                );
                                                                            })}
                                                                        </div>
                                                                    );
                                                                })()}
                                                                <div
                                                                    className="rounded border border-slate-700/60 bg-slate-900/40 p-2 text-xs text-slate-300">
                                                                    <div>当前展示：{renderRole(roleSource)}</div>
                                                                    {attachments.length > 0 && (
                                                                        <ul className="mt-1 space-y-1">
                                                                            {attachments.map((attachment) => (
                                                                                <li key={`${player.seat}-${attachment.slot}-${attachment.index}`}>
                                                                                    {resolveSlotLabel(
                                                                                        assignmentRoleId,
                                                                                        attachment.slot,
                                                                                        attachment.slot_label ?? undefined
                                                                                    )}
                                                                                    ：
                                                                                    {attachment.role ? renderRole(attachment.role) : "未选择"}
                                                                                </li>
                                                                            ))}
                                                                        </ul>
                                                                    )}
                                                                </div>
                                                            </div>
                                                          )}
                                                      </td>
                                                  )}
                                                  {isHost && (
                                                      <td className="px-4 py-2 align-top">
                                                          <div className="flex flex-col gap-2">
                                                              <textarea
                                                                  className="min-h-[3rem] w-full rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm focus:outline-none focus:ring focus:ring-emerald-500"
                                                                  value={playerNoteDrafts[player.id] ?? ""}
                                                                  onChange={(event) =>
                                                                      handlePlayerNoteDraftChange(player.id, event.target.value)
                                                                  }
                                                                  onBlur={() => void handlePlayerNoteCommit(player)}
                                                                  onKeyDown={(event) => {
                                                                      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                                                                          event.preventDefault();
                                                                          void handlePlayerNoteCommit(player);
                                                                      }
                                                                  }}
                                                                  placeholder="仅主持人可见的备注"
                                                                  disabled={playerNoteSaving[player.id]}
                                                              />
                                                              {playerNoteSaving[player.id] && (
                                                                  <span className="text-xs text-slate-400">保存中...</span>
                                                              )}
                                                          </div>
                                                      </td>
                                                  )}
                                              </tr>
                                          );
                                      })}
                                    </tbody>
                                </table>
                            </div>
                            {seatMessage && (
                                <p
                                    className={`px-5 pb-4 text-xs ${
                                        seatMessageType === "error"
                                            ? "text-rose-300"
                                            : seatMessageType === "info"
                                                ? "text-emerald-300"
                                                : "text-slate-300"
                                    }`}
                                >
                                    {seatMessage}
                                </p>
                            )}
                        </>
                    ) : (
                        <p className="px-5 py-4 text-sm text-slate-300">点击“展开”即可查看玩家座位与状态。</p>
                    )}
                </section>


                <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
                    <div className="flex items-center justify-between gap-3">
                        <h2 className="text-lg font-semibold">剧本角色列表</h2>
                        <button
                            type="button"
                            className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:border-rose-400"
                            onClick={() => setShowRoles((value) => !value)}
                        >
                            {showRoles ? "折叠" : "展开"}
                        </button>
                    </div>
                    {showRoles ? (
                        <div className="mt-4 grid gap-4 md:grid-cols-2">
                            {roleSections.map((section) => (
                                <Fragment key={section.team}>
                                    <div
                                        className="col-span-full border-t border-slate-700 pt-3 text-sm font-semibold text-slate-200">
                                        {renderTeam(section.team) || section.team}
                                    </div>
                                    {section.roles.map((role) => {
                                        const cardTone = TEAM_CARD_CLASSES[role.team ?? ""] ??
                                            "border-slate-700 bg-slate-900/60";
                                        return (
                                            <div
                                                key={role.id}
                                                className={`rounded border p-4 ${cardTone}`}
                                            >
                                                <h3 className="text-base font-semibold">
                                                    {renderRole({
                                                        id: role.id,
                                                        name: role.name,
                                                        name_localized: role.name_localized,
                                                        team: role.team,
                                                        team_label: role.team_label
                                                    })}
                                                </h3>
                                                <p className="text-xs text-slate-400">阵营：{renderTeam(role.team)}</p>
                                                <p className="mt-2 text-sm text-slate-300">{role.description ?? "暂无介绍"}</p>
                                            </div>
                                        );
                                    })}
                                </Fragment>
                            ))}
                            {!roleSections.length && (
                                <p className="col-span-full text-sm text-slate-300">剧本信息尚未加载。</p>
                            )}
                        </div>
                    ) : (
                        <p className="mt-4 text-sm text-slate-300">点击“展开”即可查看该剧本的全部角色介绍。</p>
                    )}
                </section>


                {resetDialogOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4">
                        <div
                            className="w-full max-w-sm rounded-lg border border-slate-700 bg-slate-800 p-5 text-slate-100">
                            <div className="flex items-center justify-between">
                                <h3 className="text-lg font-semibold">确认重新开始</h3>
                                <button
                                    type="button"
                                    className="rounded px-2 py-1 text-sm text-slate-300 hover:text-rose-300"
                                    onClick={() => setResetDialogOpen(false)}
                                >
                                    ×
                                </button>
                            </div>
                            <p className="mt-2 text-sm text-slate-300">
                                重置将清除当前阶段、角色分配以及当日的提名投票记录，确认要回到大厅吗？
                            </p>
                            <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
                                <button
                                    type="button"
                                    className="flex-1 rounded border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:border-slate-400 disabled:opacity-50"
                                    onClick={() => setResetDialogOpen(false)}
                                    disabled={hostActionBusy}
                                >
                                    取消
                                </button>
                                <button
                                    type="button"
                                    className="flex-1 rounded border border-rose-500 px-3 py-2 text-sm font-semibold text-rose-200 hover:bg-rose-500/10 disabled:opacity-50"
                                    onClick={handleResetConfirm}
                                    disabled={hostActionBusy}
                                >
                                    确认重置
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {gameEndDialogOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4">
                        <div
                            className="w-full max-w-sm rounded-lg border border-slate-700 bg-slate-800 p-5 text-slate-100">
                            <div className="flex items-center justify-between">
                                <h3 className="text-lg font-semibold">确认游戏结果</h3>
                                <button
                                    type="button"
                                    className="rounded px-2 py-1 text-sm text-slate-300 hover:text-rose-300"
                                    onClick={() => setGameEndDialogOpen(false)}
                                >
                                    ×
                                </button>
                            </div>
                            <p className="mt-2 text-sm text-slate-300">请选择当前游戏的最终结果。</p>
                            <div className="mt-4 grid gap-2">
                                <button
                                    type="button"
                                    className="rounded border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:border-emerald-400"
                                    onClick={() => void handleGameEnd(null)}
                                    disabled={hostActionBusy}
                                >
                                    未结束
                                </button>
                                <button
                                    type="button"
                                    className="rounded border border-emerald-500 px-3 py-2 text-sm text-emerald-200 hover:bg-emerald-500/10"
                                    onClick={() => void handleGameEnd("blue")}
                                    disabled={hostActionBusy}
                                >
                                    蓝方胜利
                                </button>
                                <button
                                    type="button"
                                    className="rounded border border-rose-500 px-3 py-2 text-sm text-rose-200 hover:bg-rose-500/10"
                                    onClick={() => void handleGameEnd("red")}
                                    disabled={hostActionBusy}
                                >
                                    红方胜利
                                </button>
                                {storytellerAvailable && (
                                    <button
                                        type="button"
                                        className="rounded border border-amber-500 px-3 py-2 text-sm text-amber-200 hover:bg-amber-500/10"
                                        onClick={() => void handleGameEnd("storyteller")}
                                        disabled={hostActionBusy}
                                    >
                                        说书人胜利
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

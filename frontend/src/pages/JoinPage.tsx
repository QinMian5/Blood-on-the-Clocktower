import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { loginUser, logoutUser, registerUser, fetchCurrentUser } from "../api/auth";
import { createRoom, fetchScripts, fetchSnapshot, joinRoom } from "../api/rooms";
import type { RoomScriptInfo } from "../api/rooms";
import { useAuthStore } from "../store/authStore";
import { useRoomStore } from "../store/roomStore";
import { clearAuthToken } from "../api/client";

export function JoinPage() {
  const navigate = useNavigate();
  const connect = useRoomStore((state) => state.connect);
  const setRoomSnapshot = useRoomStore((state) => state.setSnapshot);
  const disconnectRoom = useRoomStore((state) => state.disconnect);
  const { user, setUser } = useAuthStore();

  const [authChecked, setAuthChecked] = useState(false);
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [registerCode, setRegisterCode] = useState("");
  const [registerNickname, setRegisterNickname] = useState("");
  const [registerMessage, setRegisterMessage] = useState<string | null>(null);
  const [registerBusy, setRegisterBusy] = useState(false);

  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginMessage, setLoginMessage] = useState<string | null>(null);
  const [loginBusy, setLoginBusy] = useState(false);

  const [joinCode, setJoinCode] = useState("");
  const [playerAlias, setPlayerAlias] = useState("");
  const [joinMessage, setJoinMessage] = useState<string | null>(null);
  const [joinBusy, setJoinBusy] = useState(false);

  const [scriptId, setScriptId] = useState("");
  const [scriptOptions, setScriptOptions] = useState<RoomScriptInfo[]>([]);
  const [scriptsLoading, setScriptsLoading] = useState(false);
  const [scriptsError, setScriptsError] = useState<string | null>(null);
  const [hostDisplayName, setHostDisplayName] = useState("");
  const [createMessage, setCreateMessage] = useState<string | null>(null);
  const [createBusy, setCreateBusy] = useState(false);

  useEffect(() => {
    fetchCurrentUser()
      .then((data) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setAuthChecked(true));
  }, [setUser]);

  useEffect(() => {
    if (!user?.can_create_room) {
      setScriptOptions([]);
      setScriptId("");
      setScriptsError(null);
      setScriptsLoading(false);
      return;
    }

    let cancelled = false;
    setScriptsLoading(true);
    setScriptsError(null);
    fetchScripts()
      .then((list) => {
        if (cancelled) {
          return;
        }
        setScriptOptions(list);
        setScriptId((previous) => {
          if (previous && list.some((item) => item.id === previous)) {
            return previous;
          }
          return list[0]?.id ?? "";
        });
      })
      .catch((error) => {
        console.error("fetch scripts failed", error);
        if (cancelled) {
          return;
        }
        setScriptOptions([]);
        setScriptId("");
        setScriptsError("剧本列表加载失败，请稍后重试。");
      })
      .finally(() => {
        if (!cancelled) {
          setScriptsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [user?.can_create_room]);

  const handleRegister = async (event: FormEvent) => {
    event.preventDefault();
    setRegisterBusy(true);
    setRegisterMessage(null);
    try {
      const account = await registerUser({
        username: registerUsername.trim(),
        password: registerPassword,
        code: registerCode.trim(),
        nickname: registerNickname.trim() || undefined
      });
      setUser(account);
      setRegisterMessage("注册成功，已自动登录。");
      setRegisterUsername("");
      setRegisterPassword("");
      setRegisterCode("");
      setRegisterNickname("");
    } catch (error) {
      console.error("register failed", error);
      setRegisterMessage("注册失败，请检查信息或注册码是否可用。");
    } finally {
      setRegisterBusy(false);
    }
  };

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setLoginBusy(true);
    setLoginMessage(null);
    try {
      const account = await loginUser(loginUsername.trim(), loginPassword);
      setUser(account);
      setLoginMessage("登录成功。");
    } catch (error) {
      console.error("login failed", error);
      setLoginMessage("登录失败，请确认账号和密码。");
    } finally {
      setLoginBusy(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error("logout failed", error);
    }
    setUser(null);
    clearAuthToken();
    disconnectRoom();
  };

  const handleCreateRoom = async (event: FormEvent) => {
    event.preventDefault();
    setCreateBusy(true);
    setCreateMessage(null);
    try {
      const data = await createRoom({
        scriptId: scriptId.trim() || undefined,
        hostName: hostDisplayName.trim() || undefined
      });
      connect({ roomId: data.room_id, token: data.host_token, seat: 0 });
      try {
        const snapshot = await fetchSnapshot(data.room_id);
        setRoomSnapshot(snapshot);
      } catch (error) {
        console.error("prefetch host snapshot failed", error);
      }
      setCreateMessage(`房间创建成功，加入码：${data.join_code}`);
      setHostDisplayName("");
      navigate(`/room/${data.room_id}`);
    } catch (error) {
      console.error("create room failed", error);
      setCreateMessage("创建房间失败，请稍后重试。");
    } finally {
      setCreateBusy(false);
    }
  };

  const handleJoinRoom = async (event: FormEvent) => {
    event.preventDefault();
    setJoinBusy(true);
    setJoinMessage(null);
    try {
      const response = await joinRoom(joinCode.trim(), playerAlias.trim() || undefined);
      connect({
        roomId: response.room_id,
        token: response.player_token,
        seat: response.seat,
        playerId: response.player_id
      });
      try {
        const snapshot = await fetchSnapshot(response.room_id);
        setRoomSnapshot(snapshot);
      } catch (error) {
        console.error("prefetch join snapshot failed", error);
      }
      navigate(`/room/${response.room_id}`);
    } catch (error) {
      console.error("join room failed", error);
      setJoinMessage("加入房间失败，请检查房间信息。");
    } finally {
      setJoinBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Blood on the Clocktower</h1>
            <p className="text-sm text-slate-300">在线辅助工具 · 需注册后使用</p>
          </div>
          <div className="text-sm text-slate-300">
            {authChecked ? (
              user ? (
                <div className="flex items-center gap-3">
                  <span>
                    欢迎，<span className="font-semibold text-rose-300">{user.nickname}</span>
                  </span>
                  <button
                    className="rounded border border-slate-500 px-3 py-1 hover:border-rose-400"
                    onClick={handleLogout}
                  >
                    退出登录
                  </button>
                </div>
              ) : (
                <span>请先注册或登录以加入房间</span>
              )
            ) : (
              <span>正在检查登录状态...</span>
            )}
          </div>
        </header>

        {authChecked && !user && (
          <section className="grid gap-8 lg:grid-cols-2">
            <div className="rounded-xl bg-slate-800/70 p-6 shadow-lg">
              <h2 className="mb-4 text-xl font-semibold">注册新玩家</h2>
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="register-username">
                    用户名（字母或数字）
                  </label>
                  <input
                    id="register-username"
                    type="text"
                    value={registerUsername}
                    onChange={(event) => setRegisterUsername(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-rose-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="register-password">
                    密码（至少6位，可含符号）
                  </label>
                  <input
                    id="register-password"
                    type="password"
                    value={registerPassword}
                    onChange={(event) => setRegisterPassword(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-rose-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="register-code">
                    注册码
                  </label>
                  <input
                    id="register-code"
                    type="text"
                    value={registerCode}
                    onChange={(event) => setRegisterCode(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-rose-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="register-nickname">
                    昵称（可选）
                  </label>
                  <input
                    id="register-nickname"
                    type="text"
                    value={registerNickname}
                    onChange={(event) => setRegisterNickname(event.target.value)}
                    placeholder="留空则使用用户名"
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-rose-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded bg-rose-600 py-2 font-semibold hover:bg-rose-500 disabled:opacity-50"
                  disabled={registerBusy}
                >
                  注册并登录
                </button>
              </form>
              {registerMessage && (
                <p className="mt-3 text-sm text-slate-300">{registerMessage}</p>
              )}
            </div>

            <div className="rounded-xl bg-slate-800/70 p-6 shadow-lg">
              <h2 className="mb-4 text-xl font-semibold">已有账号登录</h2>
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="login-username">
                    用户名
                  </label>
                  <input
                    id="login-username"
                    type="text"
                    value={loginUsername}
                    onChange={(event) => setLoginUsername(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="login-password">
                    密码
                  </label>
                  <input
                    id="login-password"
                    type="password"
                    value={loginPassword}
                    onChange={(event) => setLoginPassword(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-indigo-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded bg-indigo-600 py-2 font-semibold hover:bg-indigo-500 disabled:opacity-50"
                  disabled={loginBusy}
                >
                  登录
                </button>
              </form>
              {loginMessage && <p className="mt-3 text-sm text-slate-300">{loginMessage}</p>}
            </div>
          </section>
        )}

        {authChecked && user && (
          <section className="grid gap-8 lg:grid-cols-2">
            <div className="rounded-xl bg-slate-800/70 p-6 shadow-lg">
              <h2 className="mb-4 text-xl font-semibold">加入房间</h2>
              <form onSubmit={handleJoinRoom} className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="join-code">
                    加入码
                  </label>
                  <input
                    id="join-code"
                    type="text"
                    value={joinCode}
                    onChange={(event) => setJoinCode(event.target.value)}
                    required
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="player-alias">
                    显示名称（可选，默认为昵称）
                  </label>
                  <input
                    id="player-alias"
                    type="text"
                    value={playerAlias}
                    onChange={(event) => setPlayerAlias(event.target.value)}
                    placeholder={user.nickname}
                    className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-emerald-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full rounded bg-emerald-600 py-2 font-semibold hover:bg-emerald-500 disabled:opacity-50"
                  disabled={joinBusy}
                >
                  加入房间
                </button>
              </form>
              {joinMessage && <p className="mt-3 text-sm text-slate-300">{joinMessage}</p>}
            </div>

            <div className="rounded-xl bg-slate-800/70 p-6 shadow-lg">
              <h2 className="mb-4 text-xl font-semibold">主持人功能</h2>
              {user.can_create_room ? (
                <form onSubmit={handleCreateRoom} className="space-y-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium" htmlFor="script-id">
                      选择剧本
                    </label>
                    <select
                      id="script-id"
                      value={scriptId}
                      onChange={(event) => setScriptId(event.target.value)}
                      className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-amber-500"
                      disabled={scriptsLoading || scriptOptions.length === 0}
                      required
                    >
                      {scriptsLoading ? (
                        <option value="">正在加载剧本...</option>
                      ) : scriptOptions.length > 0 ? (
                        scriptOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.name}（v{option.version}）
                          </option>
                        ))
                      ) : (
                        <option value="">暂无可用剧本</option>
                      )}
                    </select>
                    {scriptsError && (
                      <p className="mt-1 text-sm text-rose-300">{scriptsError}</p>
                    )}
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium" htmlFor="host-display-name">
                      房间内显示的主持人名称（可选）
                    </label>
                    <input
                      id="host-display-name"
                      type="text"
                      value={hostDisplayName}
                      onChange={(event) => setHostDisplayName(event.target.value)}
                      placeholder={user.nickname}
                      className="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 focus:outline-none focus:ring focus:ring-amber-500"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full rounded bg-amber-500 py-2 font-semibold text-slate-900 hover:bg-amber-400 disabled:opacity-50"
                    disabled={
                      createBusy ||
                      scriptsLoading ||
                      (scriptOptions.length > 0 && !scriptId)
                    }
                  >
                    创建房间
                  </button>
                </form>
              ) : (
                <p className="text-sm text-slate-300">
                  该账号尚未开通主持人权限。如需创建房间，请联系管理员。
                </p>
              )}
              {createMessage && <p className="mt-3 text-sm text-slate-300">{createMessage}</p>}
            </div>
          </section>
        )}
      </div>
      <div className="px-6 py-6 text-center text-xs text-slate-400">
        <Link to="/admin" className="text-emerald-400 hover:text-emerald-300">
          管理员后台
        </Link>
      </div>
    </div>
  );
}

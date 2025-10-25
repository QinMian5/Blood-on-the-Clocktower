import { FormEvent, useEffect, useState } from "react";

import {
  createRegistrationCodes,
  fetchAdminProfile,
  fetchAdminUsers,
  fetchRegistrationCodes,
  loginAdmin,
  logoutAdmin,
  updateAdminUser
} from "../api/admin";
import type { AdminUser } from "../api/types";

export function AdminPage() {
  const [loading, setLoading] = useState(true);
  const [admin, setAdmin] = useState<AdminUser | null>(null);

  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginBusy, setLoginBusy] = useState(false);

  const [userSearch, setUserSearch] = useState("");
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [updatingUserId, setUpdatingUserId] = useState<number | null>(null);

  const [codes, setCodes] = useState<string[]>([]);
  const [codesLoading, setCodesLoading] = useState(false);
  const [codeCount, setCodeCount] = useState("1");
  const [codeMessage, setCodeMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminProfile()
      .then((profile) => {
        setAdmin(profile);
        void loadUsers(profile, "");
        void loadCodes();
      })
      .catch(() => {
        setAdmin(null);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadUsers = async (currentAdmin?: AdminUser | null, searchValue?: string) => {
    if (!(currentAdmin ?? admin)) {
      return;
    }
    setUsersLoading(true);
    setUsersError(null);
    try {
      const list = await fetchAdminUsers(searchValue?.trim() || undefined);
      setUsers(list);
    } catch (error) {
      console.error("fetch admin users failed", error);
      setUsersError("用户列表加载失败，请稍后重试。");
      setUsers([]);
    } finally {
      setUsersLoading(false);
    }
  };

  const loadCodes = async () => {
    setCodesLoading(true);
    try {
      const list = await fetchRegistrationCodes();
      setCodes(list);
    } catch (error) {
      console.error("fetch registration codes failed", error);
      setCodes([]);
    } finally {
      setCodesLoading(false);
    }
  };

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setLoginBusy(true);
    setLoginError(null);
    try {
      const profile = await loginAdmin({
        username: loginUsername.trim(),
        password: loginPassword
      });
      setAdmin(profile);
      setLoginUsername("");
      setLoginPassword("");
      await loadUsers(profile, "");
      await loadCodes();
    } catch (error) {
      console.error("admin login failed", error);
      setLoginError("登录失败，请确认用户名与密码。");
    } finally {
      setLoginBusy(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logoutAdmin();
    } catch (error) {
      console.error("admin logout failed", error);
    }
    setAdmin(null);
    setUsers([]);
    setCodes([]);
  };

  const handleSearchUsers = async (event: FormEvent) => {
    event.preventDefault();
    await loadUsers(admin, userSearch);
  };

  const handleToggleCreateRoom = async (user: AdminUser) => {
    setUpdatingUserId(user.id);
    setUsersError(null);
    try {
      const updated = await updateAdminUser(user.id, {
        can_create_room: !user.can_create_room
      });
      setUsers((list) => list.map((item) => (item.id === updated.id ? updated : item)));
    } catch (error) {
      console.error("update user failed", error);
      setUsersError("权限更新失败，请稍后重试。");
    } finally {
      setUpdatingUserId(null);
    }
  };

  const handleGenerateCodes = async (event: FormEvent) => {
    event.preventDefault();
    if (!admin) {
      return;
    }
    const count = Number.parseInt(codeCount, 10);
    if (!Number.isFinite(count) || count < 1) {
      setCodeMessage("请输入有效的数量。");
      return;
    }
    setCodeMessage(null);
    setCodesLoading(true);
    try {
      const created = await createRegistrationCodes(count);
      setCodeMessage(`已生成 ${created.length} 个注册码。`);
      setCodes((list) => [...created, ...list]);
    } catch (error) {
      console.error("create registration codes failed", error);
      setCodeMessage("生成注册码失败，请稍后重试。");
    } finally {
      setCodesLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900 text-slate-200">
        <p className="text-sm">加载中…</p>
      </div>
    );
  }

  if (!admin) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100">
        <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
          <h1 className="text-center text-2xl font-semibold">管理员登录</h1>
          <form className="mt-6 space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm text-slate-300" htmlFor="admin-username">
                用户名
              </label>
              <input
                id="admin-username"
                className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-sm focus:border-rose-400 focus:outline-none"
                value={loginUsername}
                onChange={(event) => setLoginUsername(event.target.value)}
                autoComplete="username"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-slate-300" htmlFor="admin-password">
                密码
              </label>
              <input
                id="admin-password"
                type="password"
                className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-sm focus:border-rose-400 focus:outline-none"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            {loginError && <p className="text-sm text-rose-300">{loginError}</p>}
            <button
              type="submit"
              className="w-full rounded bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
              disabled={loginBusy}
            >
              {loginBusy ? "登录中…" : "登录"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-700 bg-slate-800/80">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div>
            <h1 className="text-2xl font-semibold">管理员后台</h1>
            <p className="text-sm text-slate-300">当前账户：{admin.username}</p>
          </div>
          <button
            type="button"
            className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:border-rose-400"
            onClick={() => void handleLogout()}
          >
            退出登录
          </button>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-8">
        <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-semibold">玩家权限管理</h2>
            <form className="flex flex-wrap gap-2" onSubmit={handleSearchUsers}>
              <input
                type="text"
                className="rounded border border-slate-600 bg-slate-900 px-3 py-2 text-sm focus:border-rose-400 focus:outline-none"
                placeholder="搜索用户名"
                value={userSearch}
                onChange={(event) => setUserSearch(event.target.value)}
              />
              <button
                type="submit"
                className="rounded border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:border-rose-400"
                disabled={usersLoading}
              >
                {usersLoading ? "搜索中…" : "搜索"}
              </button>
            </form>
          </div>
          {usersError && <p className="mt-3 text-sm text-rose-300">{usersError}</p>}
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm text-slate-200">
              <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-3 py-2">用户名</th>
                  <th className="px-3 py-2">昵称</th>
                  <th className="px-3 py-2">可创建房间</th>
                  <th className="px-3 py-2">创建时间</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-slate-800/60">
                    <td className="px-3 py-2 font-mono text-xs sm:text-sm">{user.username}</td>
                    <td className="px-3 py-2 text-xs sm:text-sm">{user.nickname}</td>
                    <td className="px-3 py-2">
                      <label className="inline-flex items-center gap-2 text-xs sm:text-sm">
                        <input
                          type="checkbox"
                          checked={user.can_create_room}
                          disabled={updatingUserId === user.id}
                          onChange={() => void handleToggleCreateRoom(user)}
                          className="h-4 w-4 rounded border-slate-600 bg-slate-900 text-rose-500 focus:ring-rose-500"
                        />
                        <span>{user.can_create_room ? "允许" : "禁止"}</span>
                      </label>
                    </td>
                    <td className="px-3 py-2 text-xs text-slate-400 sm:text-sm">
                      {new Date(user.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {!users.length && !usersLoading && (
                  <tr>
                    <td className="px-3 py-6 text-center text-sm text-slate-400" colSpan={4}>
                      暂无数据，请尝试搜索其他用户名。
                    </td>
                  </tr>
                )}
                {usersLoading && (
                  <tr>
                    <td className="px-3 py-6 text-center text-sm text-slate-400" colSpan={4}>
                      正在加载…
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-slate-700 bg-slate-800/60 p-5">
          <h2 className="text-lg font-semibold">注册码管理</h2>
          <form className="mt-4 flex flex-wrap items-center gap-3" onSubmit={handleGenerateCodes}>
            <label className="text-sm text-slate-300" htmlFor="code-count">
              生成数量
            </label>
            <input
              id="code-count"
              type="number"
              min={1}
              max={100}
              className="w-24 rounded border border-slate-600 bg-slate-900 px-3 py-2 text-sm focus:border-rose-400 focus:outline-none"
              value={codeCount}
              onChange={(event) => setCodeCount(event.target.value)}
            />
            <button
              type="submit"
              className="rounded border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:border-rose-400"
              disabled={codesLoading}
            >
              {codesLoading ? "生成中…" : "生成"}
            </button>
            <button
              type="button"
              className="rounded border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:border-rose-400"
              onClick={() => void loadCodes()}
              disabled={codesLoading}
            >
              刷新列表
            </button>
          </form>
          {codeMessage && <p className="mt-3 text-sm text-slate-300">{codeMessage}</p>}
          <div className="mt-4 rounded border border-slate-700 bg-slate-900/60 p-4">
            {codesLoading && <p className="text-sm text-slate-400">加载中…</p>}
            {!codesLoading && !codes.length && (
              <p className="text-sm text-slate-400">暂无未使用的注册码。</p>
            )}
            {!codesLoading && codes.length > 0 && (
              <ul className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
                {codes.map((code) => (
                  <li key={code} className="rounded border border-slate-700 bg-slate-800 px-3 py-2 font-mono text-sm text-emerald-300">
                    {code}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

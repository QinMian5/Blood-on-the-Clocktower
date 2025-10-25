import { apiClient } from "./client";
import type { AdminUser } from "./types";

export interface AdminLoginPayload {
  username: string;
  password: string;
}

export async function loginAdmin(payload: AdminLoginPayload): Promise<AdminUser> {
  const { data } = await apiClient.post("/admin/login", payload);
  return data.admin;
}

export async function logoutAdmin(): Promise<void> {
  await apiClient.post("/admin/logout", {});
}

export async function fetchAdminProfile(): Promise<AdminUser> {
  const { data } = await apiClient.get("/admin/me");
  return data;
}

export async function fetchAdminUsers(search?: string): Promise<AdminUser[]> {
  const params = search ? { search } : undefined;
  const { data } = await apiClient.get("/admin/users", { params });
  return data;
}

export async function updateAdminUser(
  userId: number,
  payload: { can_create_room?: boolean; is_admin?: boolean }
): Promise<AdminUser> {
  const { data } = await apiClient.patch(`/admin/users/${userId}`, payload);
  return data;
}

export async function fetchRegistrationCodes(): Promise<string[]> {
  const { data } = await apiClient.get("/admin/registration-codes");
  return data.codes;
}

export async function createRegistrationCodes(count: number): Promise<string[]> {
  const { data } = await apiClient.post("/admin/registration-codes", { count });
  return data.codes;
}

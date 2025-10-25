import { apiClient } from "./client";
import type { AdminProfile, AdminUser } from "./types";

export interface AdminLoginPayload {
  username: string;
  password: string;
}

export async function loginAdmin(payload: AdminLoginPayload): Promise<AdminProfile> {
  const { data } = await apiClient.post("/admin/login", payload);
  return data.admin;
}

export async function logoutAdmin(): Promise<void> {
  await apiClient.post("/admin/logout", {});
}

export async function fetchAdminProfile(): Promise<AdminProfile> {
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
  payload: { can_create_room?: boolean; nickname?: string }
): Promise<AdminUser> {
  const { data } = await apiClient.patch(`/admin/users/${userId}`, payload);
  return data;
}

export async function deleteAdminUser(userId: number): Promise<void> {
  await apiClient.delete(`/admin/users/${userId}`);
}

export async function fetchRegistrationCodes(): Promise<string[]> {
  const { data } = await apiClient.get("/admin/registration-codes");
  return data.codes;
}

export async function createRegistrationCodes(count: number): Promise<string[]> {
  const { data } = await apiClient.post("/admin/registration-codes", { count });
  return data.codes;
}

export async function downloadUserDatabase(): Promise<Blob> {
  const { data } = await apiClient.get("/admin/export/users", { responseType: "blob" });
  return data;
}

export async function downloadGameDatabase(): Promise<Blob> {
  const { data } = await apiClient.get("/admin/export/games", { responseType: "blob" });
  return data;
}

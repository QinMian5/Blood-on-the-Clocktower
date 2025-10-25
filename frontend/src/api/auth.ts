import { apiClient } from "./client";

export interface AuthUser {
  id: number;
  username: string;
  nickname: string;
  can_create_room: boolean;
}

export interface RegisterPayload {
  username: string;
  password: string;
  code: string;
  nickname?: string;
}

export async function registerUser(payload: RegisterPayload) {
  const response = await apiClient.post("/auth/register", payload);
  return response.data as AuthUser;
}

export async function loginUser(username: string, password: string) {
  const response = await apiClient.post("/auth/login", { username, password });
  return response.data as AuthUser;
}

export async function logoutUser() {
  await apiClient.post("/auth/logout", {});
}

export async function fetchCurrentUser() {
  const response = await apiClient.get("/auth/me");
  return response.data as AuthUser;
}

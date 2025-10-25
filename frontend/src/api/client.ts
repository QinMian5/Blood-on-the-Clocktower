import axios from "axios";

export const apiClient = axios.create({
  baseURL: "/api",
  withCredentials: true
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("botc_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setAuthToken(token: string) {
  localStorage.setItem("botc_token", token);
}

export function clearAuthToken() {
  localStorage.removeItem("botc_token");
}

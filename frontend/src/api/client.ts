import axios from 'axios';

// 백엔드 base URL은 반드시 환경변수에서 읽는다 (하드코딩 금지).
const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8010';

const TOKEN_STORAGE_KEY = 'golfmate.access_token';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export const apiClient = axios.create({
  baseURL,
  timeout: 5000,
});

// 로그인 상태면 모든 요청에 JWT를 자동으로 붙인다.
apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 토큰이 만료/무효화되면(401) 저장된 토큰을 지워서 다음 요청부터 로그인 화면으로 유도한다.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearStoredToken();
    }
    return Promise.reject(error);
  },
);

import axios from 'axios';

// 백엔드 base URL은 반드시 환경변수에서 읽는다 (하드코딩 금지).
const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  timeout: 5000,
});

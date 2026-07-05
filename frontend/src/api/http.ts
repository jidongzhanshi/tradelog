import axios from 'axios';
import { ElMessage } from 'element-plus';
import { t } from '../i18n';

export const http = axios.create({
  baseURL: '/api',
  timeout: 20000,
});

function readErrorMessage(payload: any): string {
  if (!payload) return t('error.noDetail');
  if (typeof payload.detail === 'string') return payload.detail;
  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item: any) => {
        const path = Array.isArray(item.loc) ? item.loc.filter((part: string) => part !== 'body').join('.') : '';
        return `${path ? `${path}: ` : ''}${item.msg || JSON.stringify(item)}`;
      })
      .join('\n');
  }
  if (payload.message) return payload.message;
  return JSON.stringify(payload);
}

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('tradelog_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const requestUrl = String(error.config?.url || '');
    const isLoginRequest = requestUrl.includes('/auth/login');
    const message = error.response
      ? readErrorMessage(error.response.data)
      : t('error.network', { message: error.message });

    if (status !== 401 || isLoginRequest) {
      ElMessage({
        message,
        type: 'error',
        duration: 6500,
        showClose: true,
      });
    }

    if (status === 401 && !isLoginRequest) {
      localStorage.removeItem('tradelog_token');
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  },
);

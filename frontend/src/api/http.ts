import axios from 'axios';
import { ElMessage } from 'element-plus';

export const http = axios.create({
  baseURL: '/api',
  timeout: 20000,
});

function readErrorMessage(payload: any): string {
  if (!payload) return '请求失败：后端没有返回错误详情';
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
    const message = error.response
      ? readErrorMessage(error.response.data)
      : `网络请求失败：${error.message}`;
    if (error.response?.status !== 401) {
      ElMessage({
        message,
        type: 'error',
        duration: 6500,
        showClose: true,
      });
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('tradelog_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

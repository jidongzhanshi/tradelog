import { http } from './http';
import type { User } from '../types';

export async function login(username: string, password: string) {
  const { data } = await http.post('/auth/login', { username, password });
  return data as { access_token: string; token_type: string };
}

export async function getMe() {
  const { data } = await http.get('/auth/me');
  return data as User;
}

export async function changePassword(old_password: string, new_password: string) {
  await http.post('/auth/change-password', { old_password, new_password });
}

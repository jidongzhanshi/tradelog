import { http } from './http';
import type { Role, User } from '../types';

export async function listUsers() {
  const { data } = await http.get('/users');
  return data as User[];
}

export async function createUser(payload: { username: string; display_name: string; role: Role; password: string; is_active: boolean }) {
  const { data } = await http.post('/users', payload);
  return data as User;
}

export async function updateUser(id: number, payload: Partial<User>) {
  const { data } = await http.put(`/users/${id}`, payload);
  return data as User;
}

export async function resetPassword(id: number, password: string) {
  await http.post(`/users/${id}/reset-password`, { password, must_change_password: true });
}

export async function deleteUser(id: number) {
  await http.delete(`/users/${id}`);
}

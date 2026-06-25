import { http } from './http';

export async function getSettings(params: Record<string, unknown> = {}) {
  const { data } = await http.get('/settings', { params });
  return data as { id: number; user_id: number; initial_capital: number; currency: string };
}

export async function updateSettings(initial_capital: number, params: Record<string, unknown> = {}) {
  const { data } = await http.put('/settings', { initial_capital, currency: 'USDT' }, { params });
  return data;
}

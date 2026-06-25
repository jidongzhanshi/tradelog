import { http } from './http';
import type { Trade } from '../types';

export type TradePayload = Omit<Trade, 'id' | 'holding_seconds' | 'created_at' | 'updated_at'> & { user_id?: number };

export async function listTrades(params: Record<string, unknown>) {
  const { data } = await http.get('/trades', { params });
  return data as Trade[];
}

export async function createTrade(payload: Partial<TradePayload>) {
  const { data } = await http.post('/trades', payload);
  return data as Trade;
}

export async function updateTrade(id: number, payload: Partial<TradePayload>) {
  const { data } = await http.put(`/trades/${id}`, payload);
  return data as Trade;
}

export async function deleteTrade(id: number) {
  await http.delete(`/trades/${id}`);
}

import { http } from './http';
import type { OverviewStats } from '../types';

export async function getOverview(params: Record<string, unknown>) {
  const { data } = await http.get('/stats/overview', { params });
  return data as OverviewStats;
}

export async function getCharts(params: Record<string, unknown>) {
  const { data } = await http.get('/stats/charts', { params });
  return data;
}

export async function getComparison(params: Record<string, unknown>) {
  const { data } = await http.get('/stats/comparison', { params });
  return data as { users: OverviewStats[]; combined: OverviewStats };
}

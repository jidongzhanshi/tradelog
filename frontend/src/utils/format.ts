import dayjs from 'dayjs';

export function money(value = 0) {
  return `${value >= 0 ? '' : '-'}${Math.abs(value).toLocaleString(undefined, { maximumFractionDigits: 2 })} USDT`;
}

export function percent(value = 0) {
  return `${value.toFixed(2)}%`;
}

export function dateTime(value?: string) {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';
}

export function duration(seconds = 0) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days ? `${days} 天 ` : ''}${hours} 小时 ${minutes} 分钟`;
}

export const directionText: Record<string, string> = { long: '做多', short: '做空' };
export const statusText: Record<string, string> = { profit: '盈利', loss: '亏损', flat: '持平' };
export const marginText: Record<string, string> = { cross: '全仓', isolated: '逐仓' };
export const contractText: Record<string, string> = { perpetual: '永续', delivery: '交割' };

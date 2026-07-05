import dayjs from 'dayjs';
import { t } from '../i18n';

export function money(value = 0) {
  return `${value >= 0 ? '' : '-'}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USDT`;
}

export function percent(value = 0) {
  return `${value.toFixed(2)}%`;
}

export function rMultiple(value = 0) {
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}R`;
}

export function rewardRisk(value = 0) {
  return value > 0 ? `1:${value.toFixed(2)}` : '-';
}

export function price(value = 0) {
  const absolute = Math.abs(value);
  const maximumFractionDigits = absolute >= 1 ? 4 : 8;
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits,
  });
}

export function dateTime(value?: string) {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';
}

export function duration(seconds = 0) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days ? `${days} ${t('time.days')} ` : ''}${hours} ${t('time.hours')} ${minutes} ${t('time.minutes')}`;
}

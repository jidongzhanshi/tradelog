import { http } from './http';

export async function exportTrades(params: Record<string, unknown>) {
  const response = await http.get('/export/trades.xlsx', { params, responseType: 'blob' });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'tradelog.xlsx';
  link.click();
  URL.revokeObjectURL(url);
}

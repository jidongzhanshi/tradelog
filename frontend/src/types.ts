export type Role = 'super_admin' | 'trader' | 'viewer';
export type Direction = 'long' | 'short';
export type TradeStatus = 'profit' | 'loss' | 'flat';

export interface User {
  id: number;
  username: string;
  display_name: string;
  role: Role;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: number;
  user_id: number;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  direction: Direction;
  order_side?: string;
  contract_type: 'perpetual' | 'delivery';
  margin_mode: 'cross' | 'isolated';
  leverage: number;
  realized_pnl: number;
  roi_percent: number;
  position_size: number;
  max_position_size: number;
  avg_open_price: number;
  avg_close_price: number;
  open_time: string;
  close_time: string;
  holding_seconds: number;
  fee: number;
  status: TradeStatus;
  note?: string;
  created_at: string;
  updated_at: string;
}

export interface OverviewStats {
  user_id?: number;
  display_name?: string;
  initial_capital: number;
  account_equity: number;
  total_pnl: number;
  total_return: number;
  win_rate: number;
  average_pnl_ratio: number;
  max_drawdown: number;
  total_trades: number;
  total_profit: number;
  total_loss: number;
  profit_factor: number;
  expectancy: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
}

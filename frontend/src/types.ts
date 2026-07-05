export type Role = 'super_admin' | 'trader';
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
  stop_loss_price: number;
  take_profit_price: number;
  risk_percent: number;
  account_equity_before: number;
  planned_risk_amount: number;
  planned_profit_amount: number;
  r_multiple: number;
  planned_rr: number;
  account_return_percent: number;
  simulated_equity_before: number;
  simulated_risk_amount: number;
  simulated_profit_target: number;
  simulated_pnl: number;
  open_time: string;
  close_time: string;
  holding_seconds: number;
  fee: number;
  status: TradeStatus;
  strategy_tag?: string;
  exit_reason?: string;
  followed_plan: boolean;
  deviation_reason?: string;
  deviation_note?: string;
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
  total_r: number;
  average_r: number;
  average_risk_percent: number;
  over_risk_count: number;
  followed_plan_count: number;
  deviation_count: number;
  plan_adherence_rate: number;
  followed_plan_average_r: number;
  deviated_average_r: number;
  simulated_total_pnl: number;
  simulated_equity: number;
  simulated_return: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
}

export interface AccountOverview extends OverviewStats {
  user_id: number;
  display_name: string;
}

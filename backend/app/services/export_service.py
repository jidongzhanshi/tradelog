from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from app.models.trade import Trade


def trades_to_workbook(sheets: dict[str, list[Trade]], summaries: dict[str, dict]) -> BytesIO:
    wb = Workbook()
    wb.remove(wb.active)

    for title, trades in sheets.items():
        ws = wb.create_sheet(title[:31])
        write_trade_sheet(ws, trades)

    if summaries:
        ws = wb.create_sheet("汇总统计")
        headers = ["名称", "本金", "账户净值", "累计盈亏", "收益率", "胜率", "交易次数", "总盈利", "总亏损", "最大回撤"]
        ws.append(headers)
        style_header(ws)
        for name, item in summaries.items():
            ws.append([
                name,
                item["initial_capital"],
                item["account_equity"],
                item["total_pnl"],
                item["total_return"],
                item["win_rate"],
                item["total_trades"],
                item["total_profit"],
                item["total_loss"],
                item["max_drawdown"],
            ])
        autosize(ws)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream


def write_trade_sheet(ws, trades: list[Trade]) -> None:
    headers = [
        "平仓时间", "交易对", "方向", "合约类型", "保证金模式", "杠杆", "已实现盈亏",
        "收益率", "平仓数量", "最大OI", "平均开仓价", "平均平仓价", "开仓时间",
        "持仓秒数", "手续费", "状态", "备注",
    ]
    ws.append(headers)
    style_header(ws)
    for trade in trades:
        ws.append([
            trade.close_time,
            trade.symbol,
            trade.direction.value,
            trade.contract_type.value,
            trade.margin_mode.value,
            trade.leverage,
            trade.realized_pnl,
            trade.roi_percent,
            trade.position_size,
            trade.max_position_size,
            trade.avg_open_price,
            trade.avg_close_price,
            trade.open_time,
            trade.holding_seconds,
            trade.fee,
            trade.status.value,
            trade.note or "",
        ])
    autosize(ws)


def style_header(ws) -> None:
    fill = PatternFill("solid", fgColor="1F2937")
    font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font


def autosize(ws) -> None:
    for column in ws.columns:
        width = max(len(str(cell.value or "")) for cell in column) + 2
        ws.column_dimensions[column[0].column_letter].width = min(width, 28)

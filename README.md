# TradeLog 交易记录复盘系统

私用交易复盘系统，支持超级管理员、交易账号、只读观察账号。系统只记录已平仓交易，按 USDT 统计盈亏，支持图表分析、用户对比和 Excel 导出。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Element Plus + ECharts
- 后端：Python + FastAPI + SQLAlchemy
- 数据库：SQLite
- 部署：Docker Compose
- 访问：推荐 Tailscale 私有网络

## 默认账号

首次启动会自动创建超级管理员：

```text
用户名：admin
密码：admin123
```

建议首次登录后立刻修改密码。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

开发访问：

```text
http://localhost:5173
```

## Docker 部署

```bash
cp .env.example .env
docker compose up -d --build
```

访问：

```text
http://服务器IP:8080
```

Docker 部署时，数据会持久化在：

```text
data/tradelog.db
data/backups/
```

本地开发不使用 Docker 时，后端默认数据库在：

```text
C:\Users\<你的用户名>\AppData\Local\TradeLog\data\tradelog.db
```

## 主要功能

- 用户登录与 JWT 鉴权
- 超级管理员用户管理
- 交易记录新增、编辑、删除、筛选、排序
- 只读观察账号查看多用户与对比数据
- 总览面板、权益曲线、月度盈亏、盈亏分布、币种排行、多空对比
- Excel 导出
- SQLite 数据持久化和手动备份接口

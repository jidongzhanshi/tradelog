# TradeLog 交易记录复盘系统

TradeLog 是一个私用交易记录与复盘系统，支持超级管理员、多交易账户数据隔离、图表分析、Excel 导出和本地 SQLite 数据持久化。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Element Plus + ECharts + GSAP
- 后端：Python 3.12 + FastAPI + SQLAlchemy
- 数据库：SQLite
- 部署：Docker Compose
- 访问方式：Tailscale Funnel

## 默认账号

首次启动会自动创建超级管理员：

```text
用户名：admin
密码：admin123
```

公开访问前请务必在 `.env` 中修改默认密码和 `SECRET_KEY`。

## 本地开发

### 后端

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

Vite 6 需要 Node.js 18 / 20 / 22+。如果使用 nvm-windows，推荐：

```powershell
nvm install 20
nvm use 20
```

启动前端：

```powershell
cd frontend
npm install
npm run dev
```

开发访问地址：

```text
http://localhost:5173
```

## Docker 部署

```bash
cp .env.example .env
docker compose up -d --build
```

默认本机访问地址：

```text
http://服务器IP:8080
```

Docker 部署时，数据会持久化在：

```text
data/tradelog.db
data/backups/
```

本地非 Docker 开发时，后端默认数据目录在：

```text
C:\Users\<你的用户名>\AppData\Local\TradeLog\data\
```

## 树莓派 + Tailscale Funnel

后续正式部署建议参考 [README_DEPLOY.md](README_DEPLOY.md)。

推荐效果：

```text
朋友打开 https://你的设备名.你的tailnet.ts.net
无需安装 Tailscale
无需公网 IP
无需路由器端口映射
```

## 主要功能

- 用户登录与 JWT 鉴权
- 超级管理员工作台、用户管理、多账户对比
- 交易账户只能查看和维护自己的数据
- 交易记录新增、编辑、删除、筛选、排序
- 中英文与明暗主题切换
- 总览面板、权益曲线、月度盈亏、盈亏分布、币种排行、多空对比
- Excel 导出
- SQLite 数据持久化、版本迁移和手动备份接口

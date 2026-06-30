# TradeLog 部署说明：树莓派 + Docker + Tailscale Funnel

本文档面向后续部署到树莓派的方案。

目标效果：

```text
TradeLog 跑在树莓派 Docker 中
本机服务地址：http://localhost:8080
公网访问地址：https://<设备名>.<tailnet名>.ts.net
朋友不用安装 Tailscale，直接打开 HTTPS 链接即可使用
```

## 0. 方案说明

本项目使用 Docker Compose 部署：

- `backend`：FastAPI，容器内端口 `8000`
- `frontend`：Nginx + 前端静态文件，宿主机端口 `8080`
- `data/`：SQLite 数据与备份文件

Tailscale Funnel 的作用是把公网 HTTPS 入口转发到树莓派本地的 `http://127.0.0.1:8080`。

注意：

- Tailscale Funnel 是公网访问方案，任何拿到链接的人都可能访问登录页。
- 公开前必须修改默认管理员密码和 `SECRET_KEY`。
- 不要把 `.env`、数据库文件或备份文件提交到公开仓库。

## 1. 准备树莓派系统

推荐：

```text
Raspberry Pi OS 64-bit
```

更新系统：

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl ca-certificates
```

## 2. 安装 Docker

使用 Docker 官方安装脚本：

```bash
curl -fsSL https://get.docker.com | sh
```

把当前用户加入 `docker` 组：

```bash
sudo usermod -aG docker $USER
```

退出 SSH 后重新登录，验证：

```bash
docker version
docker compose version
```

## 3. 安装 Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

按照终端提示打开登录链接，在浏览器里登录你的 Tailscale 账号。

验证：

```bash
tailscale status
tailscale ip -4
```

## 4. 在 Tailscale 管理后台启用 Funnel

登录 Tailscale 管理后台：

```text
https://login.tailscale.com/admin
```

确认以下设置：

1. 开启 MagicDNS
2. 开启 HTTPS certificates
3. 在 Access controls / ACL policy 中允许 Funnel

如果你的 tailnet policy 中没有 `nodeAttrs`，可以加入类似配置：

```json
{
  "nodeAttrs": [
    {
      "target": ["*"],
      "attr": ["funnel"]
    }
  ]
}
```

如果你只想允许树莓派这台设备使用 Funnel，可以在 Tailscale 后台按设备或标签收紧权限。

## 5. 部署 TradeLog

克隆项目：

```bash
cd ~
git clone <你的仓库地址> tradelog
cd tradelog
```

如果你是手动上传项目，请确保当前目录里有：

```text
docker-compose.yml
backend/
frontend/
.env.example
```

创建配置：

```bash
cp .env.example .env
nano .env
```

至少修改这些值：

```env
APP_PORT=8080
SECRET_KEY=换成一长串随机字符串
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=换成强密码
CORS_ORIGINS=*
BACKUP_KEEP_DAYS=30
```

生成随机 `SECRET_KEY` 可以用：

```bash
openssl rand -hex 32
```

启动：

```bash
docker compose up -d --build
```

检查：

```bash
docker compose ps
docker compose logs -f
```

本机验证：

```bash
curl http://localhost:8080
curl http://localhost:8080/health
```

同一局域网内也可以先访问：

```text
http://树莓派局域网IP:8080
```

## 6. 启用 Tailscale Funnel

先确认本地服务已经正常：

```bash
curl http://localhost:8080
```

启动 Funnel，把公网 HTTPS 入口转发到本地 8080：

```bash
sudo tailscale funnel --bg 8080
```

查看 Funnel 状态：

```bash
tailscale funnel status
```

预期会看到一个类似这样的地址：

```text
https://<设备名>.<tailnet名>.ts.net
```

把这个 HTTPS 地址发给朋友即可。

## 7. 停止或修改 Funnel

停止 Funnel：

```bash
sudo tailscale funnel reset
```

如果只是想取消后台运行后重新配置，可以先 reset，再重新执行：

```bash
sudo tailscale funnel --bg 8080
```

## 8. 日常更新

```bash
cd ~/tradelog
git pull
docker compose up -d --build
```

查看运行状态：

```bash
docker compose ps
docker compose logs -f
tailscale funnel status
```

## 9. 数据备份

最重要的目录是：

```text
data/
```

其中包含：

```text
data/tradelog.db
data/backups/
```

建议定期备份：

```bash
tar -czf tradelog-data-$(date +%F).tar.gz data/
```

可以把备份文件复制到另一台机器、移动硬盘或云盘。

## 10. 常见问题

### 朋友打开链接看到登录页，但登录失败

确认 `.env` 里的默认管理员密码，或者登录后在系统里重置用户密码。

### Funnel 地址打不开

依次检查：

```bash
docker compose ps
curl http://localhost:8080
tailscale status
tailscale funnel status
```

并确认 Tailscale 管理后台已经允许 Funnel。

### 树莓派重启后服务没有恢复

Docker Compose 中服务已配置 `restart: unless-stopped`，正常会自动恢复。

如果 Funnel 没有恢复，重新执行：

```bash
sudo tailscale funnel --bg 8080
```

### 需要更安全的公开访问

当前应用本身有登录系统。公开给朋友使用时，至少做到：

- 修改默认管理员密码
- 使用强 `SECRET_KEY`
- 不共享管理员账号
- 定期备份 `data/`
- 不把 `.env` 和 `data/` 提交到公开仓库

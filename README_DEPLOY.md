# 部署说明

## 1. Windows Server 测试部署

准备：

```text
Docker Desktop / Docker Engine
Git
Tailscale，可选
```

部署：

```bash
git clone <你的仓库地址> tradelog
cd tradelog
copy .env.example .env
docker compose up -d --build
```

访问：

```text
http://WindowsServer-IP:8080
```

如果开启 Tailscale，则访问：

```text
http://WindowsServer-Tailscale-IP:8080
```

## 2. 树莓派部署

准备 Raspberry Pi OS 64-bit，并安装 Docker、Docker Compose、Git、Tailscale。

安装 Tailscale：

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

部署：

```bash
git clone <你的仓库地址> tradelog
cd tradelog
cp .env.example .env
docker compose up -d --build
```

访问：

```text
http://树莓派Tailscale-IP:8080
```

## 3. 更新系统

```bash
cd tradelog
git pull
docker compose up -d --build
```

## 4. 备份重点

最重要的是备份：

```text
data/
```

其中包含：

```text
data/tradelog.db
data/backups/
```

代码可以重新拉取，数据库文件不能丢。

本地开发时使用的数据库默认位于：

```text
C:\Users\<你的用户名>\AppData\Local\TradeLog\data\tradelog.db
```

Docker 部署时会通过环境变量切换到：

```text
data/tradelog.db
```

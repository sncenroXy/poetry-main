#!/bin/bash
# 诗词雅韵 - 一键部署脚本
# 用法: bash deploy.sh [first|update]

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
    info "Docker 安装完成"
fi

if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose 未安装（需要 Docker Compose V2）"
    exit 1
fi

case "${1:-update}" in
    first)
        info "=== 首次部署 ==="

        # Create .env from template if not exists
        if [ ! -f .env ]; then
            cp .env.example .env
            warn "已创建 .env 文件，请编辑填入实际的 API Key："
            warn "  vi .env"
            warn "编辑完成后重新运行: bash deploy.sh first"
            exit 0
        fi

        info "构建并启动所有服务..."
        docker compose up -d --build

        info "=== 部署完成 ==="
        info "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
        info "查看日志: docker compose logs -f"
        ;;

    update)
        info "=== 更新部署 ==="

        # Pull latest code (if using git)
        if [ -d .git ]; then
            info "拉取最新代码..."
            git pull
        fi

        info "重新构建并启动..."
        docker compose up -d --build

        info "清理旧镜像..."
        docker image prune -f

        info "=== 更新完成 ==="
        ;;

    stop)
        info "停止所有服务..."
        docker compose down
        info "服务已停止"
        ;;

    logs)
        docker compose logs -f
        ;;

    status)
        docker compose ps
        ;;

    *)
        echo "用法: bash deploy.sh [first|update|stop|logs|status]"
        echo "  first  - 首次部署（安装 Docker、创建 .env、构建启动）"
        echo "  update - 更新部署（拉取代码、重新构建）"
        echo "  stop   - 停止所有服务"
        echo "  logs   - 查看实时日志"
        echo "  status - 查看服务状态"
        ;;
esac

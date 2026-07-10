# ============================================
# HPMS Backend Dockerfile — uv 构建
# ============================================
# 构建前请先生成 uv.lock：
#   cd backend && uv lock
#
# 使用 uv 的多阶段构建，比 pip 快 10-100 倍，且具有确定性

FROM python:3.11-slim AS builder

# 安装 uv（Astral 出品的高性能 Python 包管理器）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 安装系统编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 只复制依赖文件，充分利用 Docker 缓存层
COPY pyproject.toml uv.lock* ./

# 安装依赖（--frozen 使用 uv.lock 精确锁定版本）
RUN uv sync --frozen --no-dev --no-editable

# ========== 运行阶段 ==========
FROM python:3.11-slim

WORKDIR /app

# 安装运行时系统依赖（仅需 mysql client，不需要 gcc）
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 .venv 虚拟环境
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 复制应用代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

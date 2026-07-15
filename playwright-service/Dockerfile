# ============================================
# Playwright Service Dockerfile — uv 构建
# ============================================
# DISCLAIMER: For personal/family use only.
# Commercial use and high-frequency crawling are strictly prohibited.

FROM mcr.microsoft.com/playwright:v1.42.0-focal AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 安装 Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --no-editable

# ========== 运行阶段 ==========
FROM mcr.microsoft.com/playwright:v1.42.0-focal

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8080

CMD ["python3", "-m", "http.server", "8080"]

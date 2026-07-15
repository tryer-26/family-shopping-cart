# 🛒 HPMS - 家庭采购决策系统 (Family Shopping Decision System)

> **声明：本系统仅限个人/家庭用途，禁止商用与高频爬取。**
>
> DISCLAIMER: This system is for personal/family use only.
> Commercial use and high-frequency crawling are strictly prohibited.

## 系统概述

家庭采购决策系统（HPMS）是一套面向家庭的采购管理平台，解决"不知道缺什么、不知道哪里最便宜、优惠券过期、囤货时机、重复比价"等日常采购痛点。

**核心功能：**
- 👨‍👩‍👧‍👦 多家庭多用户协作管理
- 📦 商品库与分类管理
- 📋 采购清单（一键补货）
- 💰 多平台价格跟踪与比价
- 🎫 优惠券管理（到期提醒）
- 📷 识图搜品（阿里云OCR）
- 🔍 全文搜索（Meilisearch）
- 📊 数据统计与报表导出

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python 3.11+) |
| 数据库 | MySQL 8 |
| 搜索引擎 | Meilisearch |
| 异步任务 | Celery + Redis |
| 浏览器自动化 | Playwright（独立容器） |
| OCR/识图 | 阿里云 OCR（可降级Mock） |
| 文件存储 | 阿里云 OSS（可降级Mock） |
| 前端 | Vue 3 + Element Plus + Vite |
| 反向代理 | Nginx |
| 部署 | Docker + docker-compose |

## 快速开始

### 前置要求
- Docker & Docker Compose
- Git

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd family-shopping-cart
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，按需修改数据库密码、密钥等配置
```

### 3. 启动服务

```bash
docker-compose up -d
```

启动后访问：
- **前端页面**：http://localhost
- **API文档**：http://localhost/docs
- **Meilisearch管理**：http://localhost:7700

### 4. 使用步骤

1. 注册账号 -> 创建家庭 -> 初始化默认分类
2. 在商品库中添加商品和采购方案
3. 在采购清单中添加待购商品
4. 配置优惠券和价格渠道
5. 查看价格看板和数据报表

## 需要配置的服务

以下服务在首次启动时可使用 Mock 模式运行，
生产环境需要配置真实密钥：

| 服务 | 配置项 | 说明 |
|------|--------|------|
| MySQL | `.env`中`MYSQL_*` | Docker自动创建 |
| Redis | `.env`中`REDIS_*` | Docker自动创建 |
| Meilisearch | `MEILISEARCH_*` | Docker自动创建 |
| **阿里云OSS** | `OSS_ACCESS_KEY_ID/SECRET` | 用于图片存储，可选 |
| **阿里云OCR** | `OCR_ACCESS_KEY_ID/SECRET` | 用于识图搜品，可选 |

### ⚠️ 注册阿里云账号后需配置
1. **OSS**: 创建 Bucket，设置权限为公共读
2. **OCR**: 开通"商品识别"API服务
3. 将生成的 AccessKey 填入 `.env` 文件

## 项目结构

```
family-shopping-cart/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   ├── schemas/      # Pydantic 数据验证
│   │   ├── crud/         # 数据库操作层
│   │   ├── routers/      # API 路由
│   │   ├── services/     # 业务服务层
│   │   ├── tasks/        # Celery 异步任务
│   │   └── utils/        # 工具函数
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API 接口层
│   │   ├── stores/       # Pinia 状态管理
│   │   └── router/       # 路由配置
│   ├── Dockerfile
│   └── nginx/            # Nginx 配置
├── playwright-service/   # Playwright 浏览器自动化
├── docker-compose.yaml   # Docker 编排
└── .env.example          # 环境变量模板
```

## API 概览

| 模块 | 基础路径 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth/` | 注册、登录、Token刷新 |
| 家庭管理 | `/api/v1/families/` | 家庭CRUD、成员管理 |
| 分类管理 | `/api/v1/categories/` | 分类树、排序 |
| 商品管理 | `/api/v1/products/` | 商品CRUD、采购方案 |
| 价格管理 | `/api/v1/prices/` | 价格渠道、历史、抓取 |
| 优惠券 | `/api/v1/coupons/` | 优惠券CRUD、过期提醒 |
| 采购清单 | `/api/v1/shopping-list/` | 清单项、批量操作 |
| 搜索 | `/api/v1/search/` | Meilisearch全文搜索 |
| 识图搜品 | `/api/v1/ocr/` | 图片上传、OCR识别 |
| 数据统计 | `/api/v1/statistics/` | 仪表盘、月度报表 |
| 导出 | `/api/v1/export/` | CSV/Excel/PDF导出 |
| 系统设置 | `/api/v1/system/` | 配置管理 |

## 许可证

MIT License

---
*Made with ❤️ for family life*

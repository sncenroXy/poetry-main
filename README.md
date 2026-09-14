# 诗词雅韵

中国古典诗词学习与创作平台，融合 AI 能力，提供诗词检索、鉴赏、AI 创作、飞花令 AI 对战、答题闯关、诗画互生、诗境漫游、诗境动画等功能。

## 技术栈

- **前端**: Vue 3 + Vite 5 + Tailwind CSS 3 + Vant 4 + Pinia
- **后端**: Python FastAPI + Uvicorn + Motor (异步 MongoDB 驱动)
- **数据库**: MongoDB 7
- **AI**: OpenAI 兼容接口 (文本生成 / 图像生成 / 视觉理解 / 视频生成)
- **部署**: Docker Compose + Nginx 反向代理

## 功能模块

| 模块 | 说明 |
|------|------|
| 诗词检索 | 按诗名、作者、诗句、意象模糊搜索，支持朝代/体裁/作者/标签分类筛选，分页浏览 |
| 诗词鉴赏 | 原文、白话译文、赏析、文化拓展、作者简介 |
| AI 创作 | 根据场景/情感/风格/意象生成古典诗词 |
| 诗词润色 | 对已有诗词进行 AI 润色优化 |
| 仿写工坊 | 参考原诗，AI 仿写新篇 |
| 飞花令 | 诗词接龙挑战：经典模式（数据库匹配）/ AI 对战模式（AI 接句出题），支持渐进提示、语义校验 |
| 答题闯关 | 数据库填空题 + AI 多题型生成（填空/上下句/作者识别/意境判断），支持 AI 逐题解析与总结分析 |
| 诗画互生 | 诗词生成水墨配图（文生图）/ 图片生成诗词（图生文） |
| 诗境漫游 | AI 意象分析 + 星图可视化，沉浸式探索诗词意象网络 |
| 诗境动画 | 基于诗词意境生成短视频（智谱 CogVideoX） |
| AI 诗词助手 | 首页对话式 AI 助手，支持诗词赏析、典故解说、学习答疑 |

## 快速开始 (本地开发)

### 前置要求

- Node.js >= 18
- Python >= 3.10
- MongoDB >= 6

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env         # 编辑 .env 填入 API Key
python run.py
```

后端运行在 `http://localhost:8081`，API 文档: `http://localhost:8081/docs`

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

## Docker 部署

### 1. 克隆代码

```bash
git clone https://github.com/your-username/poetry.git
cd poetry
```

### 2. 配置环境变量

```bash
cp .env.example .env
vi .env    # 填入 LLM_API_KEY、IMAGE_API_KEY 等
```

### 3. 一键部署

```bash
bash deploy.sh first
```

### 4. 导入数据

从本地 MongoDB Compass 导出 `poems` 集合为 JSON 后：

```bash
# 上传数据文件到服务器
scp poems.json user@server:~/poetry/

# 导入到 Docker 中的 MongoDB
docker compose cp poems.json poetry-mongo:/tmp/poems.json
docker compose exec poetry-mongo mongoimport \
  --db poetrydb --collection poems \
  --file /tmp/poems.json --jsonArray --drop
```

### 5. 验证

```bash
# 查看服务状态
bash deploy.sh status

# 查看日志
bash deploy.sh logs
```

访问 `http://服务器IP` 即可使用。

## 部署架构

```
用户浏览器 :80
    │
    ▼
  Nginx (poetry-web)
  ├── /        → Vue SPA 静态文件
  └── /api/*   → 反向代理
                    │
                    ▼
              FastAPI (poetry-api) :8081
                    │
                    ▼
              MongoDB (poetry-mongo) :27017
```

## 常用命令

```bash
bash deploy.sh first    # 首次部署
bash deploy.sh update   # 更新部署 (git pull + rebuild)
bash deploy.sh stop     # 停止服务
bash deploy.sh logs     # 查看日志
bash deploy.sh status   # 查看状态
```

## API 接口

### 检索与浏览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/search?q=明月` | 通用检索（诗句/诗名/作者/意象） |
| GET | `/api/poems?page=1` | 诗词列表（支持 dynasty/genre/author/tag 筛选） |
| GET | `/api/poems/filters` | 获取筛选项（朝代、体裁、作者、标签） |
| GET | `/api/poems/{id}` | 诗词详情 |
| GET | `/api/authors/{name}/poems` | 按作者查询 |
| GET | `/api/poem/{id}/detail` | 鉴赏详情（译文、赏析、文化拓展） |

### AI 创作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | AI 生成诗词 |
| POST | `/api/generate/optimize` | 润色诗词 |
| POST | `/api/generate/mimic` | 仿写诗词 |

### 飞花令

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/challenge/chain/next?line=...` | 查找下句候选 |
| POST | `/api/challenge/chain/validate` | 精确校验接龙 |
| POST | `/api/challenge/chain/ai-hint` | AI 渐进提示（level 1-3） |
| POST | `/api/challenge/chain/ai-validate` | AI 语义校验 |
| POST | `/api/challenge/chain/ai-turn` | AI 对战回合（接句+出题） |

### 答题闯关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/challenge/quiz?count=5` | 数据库生成填空题 |
| POST | `/api/challenge/quiz/ai-generate` | AI 生成多题型 |
| POST | `/api/challenge/quiz/ai-explain` | AI 解析单题 |
| POST | `/api/challenge/quiz/ai-summary` | AI 答题总结 |

### 诗画互生

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/image/generate` | 诗词生成配图（文生图） |
| POST | `/api/image/poem` | 图片生成诗词（图生文） |

### 诗境漫游 & 动画

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/imagery/analyze` | AI 意象分析（节点+关联+文化含义） |
| POST | `/api/video/generate` | 提交诗境动画生成任务 |
| GET | `/api/video/status/{task_id}` | 查询视频生成状态 |

### AI 助手

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/assistant/chat` | 诗词助手对话 |

## 环境变量

参见 [.env.example](.env.example)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WEB_PORT` | Nginx 对外端口 | `80` |
| `MONGODB_URI` | MongoDB 连接地址 | `mongodb://mongo:27017` |
| `DATABASE_NAME` | 数据库名 | `poetrydb` |
| `LLM_API_KEY` | 文本生成 API Key | - |
| `LLM_BASE_URL` | 文本生成 API 地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 文本生成模型 | `gpt-4o-mini` |
| `IMAGE_API_KEY` | 图像生成 API Key | - |
| `IMAGE_BASE_URL` | 图像生成 API 地址 | `https://open.bigmodel.cn/api/paas/v4/` |
| `IMAGE_MODEL` | 图像生成模型 | `Cogview-3-Flash` |
| `IMAGE_SIZE` | 图像尺寸 | `1024x1024` |
| `VISION_API_KEY` | 视觉模型 API Key | - |
| `VISION_BASE_URL` | 视觉模型 API 地址 | `https://api.openai.com/v1` |
| `VISION_MODEL` | 视觉模型 | `gpt-4o` |
| `VIDEO_API_KEY` | 视频生成 API Key | - |
| `VIDEO_BASE_URL` | 视频生成 API 地址 | `https://open.bigmodel.cn/api/paas/v4/` |
| `VIDEO_MODEL` | 视频生成模型 | `cogvideox-flash` |

## License

MIT

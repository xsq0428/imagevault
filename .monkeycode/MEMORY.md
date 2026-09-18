# User Instruction Memory

This file records user instructions, preferences, and teachings for reference in future interactions.

## Format

### User Instruction Entry
[User Instruction Summary]
- Date: [YYYY-MM-DD]
- Context: [Mentioned scenario or time]
- Instructions:
  - [Content of user teaching or instruction, described line by line]

### Project Knowledge Entry
[Project Knowledge Summary]
- Date: [YYYY-MM-DD]
- Context: Discovered by Agent while performing [specific task description]
- Category: [Operations & Deployment|Build Methods|Testing Methods|Troubleshooting & Debugging|Workflow & Collaboration|Environment Configuration]
- Instructions:
  - [Specific knowledge points, described line by line]

## Deduplication Strategy
- Before adding a new entry, check for similar or identical instructions.
- If a duplicate is found, skip the new entry or merge it with the existing one.
- When merging, update the context or date information.
- This helps avoid redundant entries and keeps the memory file tidy.

## Entries

[Project Knowledge Summary]
- Date: 2026-09-18
- Context: Discovered by Agent while building the ImageVault image preview project
- Category: Build Methods
- Instructions:
  - 前端目录为 `/workspace/frontend`，生产构建命令为 `npm --prefix /workspace/frontend run build`
  - 后端无编译步骤，入口为 `app.main:app`
  - 前端构建属于 Node.js 构建任务，需通过受资源限制的后台终端执行

[Project Knowledge Summary]
- Date: 2026-09-18
- Context: Discovered by Agent while starting the ImageVault services
- Category: Operations & Deployment
- Instructions:
  - 后端启动命令：`python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir /workspace/backend`
  - 后端必须传 `--app-dir /workspace/backend`，因为工作目录不是 backend 目录
  - 前端启动命令：`npm --prefix /workspace/frontend run dev`，端口 5173，`/api` 由 Vite 反向代理到 8000
  - 图片原图、缩略图与 SQLite 文件统一位于 `/workspace/backend/data/`
  - 前台路由为 `/`，后台入口为 `/admin/dashboard`
  - 数据库新增列通过 `app/database.py` 的 `run_migrations` 在启动时以 ALTER TABLE 补齐，不重建库

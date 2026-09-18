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

[Project Knowledge Summary]
- Date: 2026-09-18
- Context: Discovered by Agent while merging frontend/backend ports and adding admin auth
- Category: Operations & Deployment
- Instructions:
  - 生产模式只需启动 8000：FastAPI 挂载 `frontend/dist` 并做 SPA 回退，同时提供 `/api`；Nginx 只需反代到 8000，无需再起 5173
  - 修改前端后必须先执行 `npm --prefix /workspace/frontend run build`，否则 8000 仍提供旧静态文件
  - 登录入口 `/admin/login`，会话使用 HttpOnly Cookie；首次启动若无管理员会自动创建，密码可在「站点配置」页修改
  - 忘记密码的处理：停止服务后清空 `admin_users` 表记录，重启会重新创建默认管理员
  - 数字验证码答案保存在进程内存，必须单进程（单 worker）运行，多 worker 会导致验证码校验失败

[User Instruction Summary]
- Date: 2026-09-18
- Context: User requested admin login feature and site configuration
- Instructions:
  - 前台（首页、分类、套图详情）保持公开访问，不添加登录页，也不做登录拦截
  - 登录页仅属于后台，路由为 `/admin/login`，只保护 `/admin` 下的管理接口与页面
  - 站点配置需包含：站点名称与标语、描述与 SEO 关键词、页脚版权与备案号、Logo 上传、前台每页显示数量、首页公告

[Project Knowledge Summary]
- Date: 2026-09-18
- Context: Agent 在调试数据库迁移时误删 gallery.db 导致用户数据丢失，事后补充的保护措施
- Category: Troubleshooting & Debugging
- Instructions:
  - 严禁删除 `/workspace/backend/data/gallery.db`；新增字段一律通过 `app/database.py` 的 `run_migrations` 用 ALTER TABLE 补齐，不得重建库
  - 若确需重建测试库，必须先把 gallery.db 复制到 `/tmp/opencode/` 备份，并先与用户确认
  - 服务启动时会自动把数据库备份到 `/workspace/backend/data/backups/`（保留最近 20 份），由 `database.backup_database()` 实现
  - 图片原图存放在 `data/originals/`，缩略图在 `data/thumbs/`；两者与 DB 解耦，DB 丢失时可依据原图重建 images 记录（分类/套图/标签/横幅等元数据无法从文件恢复）

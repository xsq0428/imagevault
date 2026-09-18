# 开发指南

## 环境要求

- Node.js 18+ 与 npm
- Python 3.10+

## 快速开始

```bash
# 安装后端依赖
pip3 install --break-system-packages -r backend/requirements.txt

# 安装前端依赖
cd frontend && npm install

# 同时启动前后端
bash start.sh
```

后端运行在 `http://127.0.0.1:8000`，前端运行在 `http://127.0.0.1:5173`，前端的 `/api` 请求由 Vite 反向代理到后端。

## 项目结构说明

```
backend/
  app/main.py             FastAPI 入口，注册路由与初始化数据库
  app/models.py           Image / Tag 数据模型
  app/image_store.py      文件落盘与缩略图生成
  app/routers/images.py   图片与标签接口
  data/                   运行时生成的原图、缩略图与 SQLite 文件
frontend/
  src/App.vue             页面状态编排
  src/api.js              接口封装
  src/components/         顶栏、侧边分类、网格、分页、灯箱、上传弹窗
```

## 开发规范

- 前端组件使用 `<script setup>` 组合式 API，样式写在组件 `<style scoped>` 中
- 后端新增接口统一放在 `app/routers/` 下并挂载到 `/api` 前缀
- 图片文件只通过 `image_store` 读写，避免绕过缩略图生成逻辑

## 设计规范

整体采用「画廊中性风，图像优先」：界面用黑白灰中性色，让图片成为主视觉；品牌绿仅作为唯一强调色，用于选中态、主按钮与指示条。

设计 token 定义在 `frontend/src/styles.css` 的 `:root`：

| 变量 | 值 | 用途 |
|------|-----|------|
| `--mint-50` | `#fafafa` | 页面背景 |
| `--mint-100` | `#edf4ef` | 浅色面、标签底、侧栏底 |
| `--mint-200` | `#e2e8e4` | 浅边框 |
| `--mint-500` | `#26794b` | 强调色（主按钮、选中态、指示条） |
| `--mint-600` | `#1f6b41` | 强调色文字与悬停 |
| `--ink-900` | `#18181b` | 主文字 |
| `--ink-700` | `#3f3f46` | 次级标题 |
| `--ink-500` | `#64748b` | 次要文字 |
| `--ink-300` | `#94a3b8` | 弱化文字 |
| `--line` | `#e4e4e7` | 分割线与边框 |
| `--shadow-card` | `0 1px 2px rgba(24,24,27,.05)` | 卡片极浅阴影 |
| `--radius-md` / `--radius-lg` | `12px` / `18px` | 圆角 |

约定：
- 组件内不写死品牌色，统一引用 token
- 图标使用内联 SVG，不使用 emoji
- 交互元素保留 `:focus-visible` 轮廓，并尊重 `prefers-reduced-motion`
- 可点击区域不小于 44×44px，底部固定栏为内容预留安全内边距

## 响应式断点

统一使用三档断点，所有页面按此适配：

| 档位 | 宽度 | 导航形态 | 网格 |
|------|------|----------|------|
| 手机 | `< 768px` | 底部标签栏 | 2 列 |
| 平板 | `768px – 1023px` | 底部标签栏 | 3 列 |
| 电脑 | `>= 1024px` | 左侧固定侧边栏 | 4 列（≥1360px 为 5 列） |

**前台**
- 公共骨架为 `FrontLayout`：桌面显示 `AppSidebar` 左侧导航，移动端隐藏侧栏并显示 `BottomTabBar`
- 首页：广告在桌面加左右边距与圆角并限制最大高度；分类卡 3 / 4 / 5 / 6 列递进
- 分类页：搜索栏吸顶，左侧分类栏吸顶固定，右侧列表随页面滚动；分类栏宽度 96 / 120 / 150
- 套图详情：桌面改为左右分栏，封面在左且吸顶，信息与成员网格在右

**后台**
- 手机：侧边栏为抽屉，默认收起，表格转为卡片堆叠
- 平板：侧边栏收为 74px 纯图标，内容区全宽
- 电脑：侧边栏 236px，内容居中且最大宽度 1280px

**兜底**
- 后台 `.admin-shell` 使用 `overflow-x: clip` 防止横向溢出
- 表格在中等宽度包裹于 `.table-wrap`，最多表格自身横向滚动


## 常见任务

```bash
# 仅启动后端
python3 -m uvicorn app.main:app --reload --port 8000
```

```bash
# 仅启动前端
npm run dev
```

## 构建与发布

```bash
# 前端生产构建
npm run build
```

生产部署时把 `frontend/dist` 交给任意外部可用的静态服务器托管，并将 `/api` 反向代理到 FastAPI 进程。后端无需额外编译步骤。

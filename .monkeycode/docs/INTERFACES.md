# 接口定义

所有接口以 `/api` 为前缀。成功响应使用 JSON；媒体接口直接返回图片字节。

## 数据对象

图片：

```json
{
  "id": 1,
  "filename": "sunset.jpg",
  "stored_name": "a1b2c3.jpg",
  "content_type": "image/jpeg",
  "width": 4032,
  "height": 3024,
  "size": 2048000,
  "description": "",
  "placeholder": "data:image/jpeg;base64,...",
  "category_id": 2,
  "category_name": "风景",
  "tags": ["旅行", "晚霞"],
  "deleted_at": null,
  "created_at": "2026-09-18T12:00:00"
}
```

分类：

```json
{ "id": 2, "name": "风景", "description": "自然风光", "sort_order": 1, "image_count": 12, "cover_source": "image", "cover_image_id": 18, "cover_placeholder": "data:image/jpeg;base64,..." }
```

`cover_source` 取值：`upload`（管理员上传的封面）、`image`（该分类最新素材缩略图）、`none`（无封面）。

## 图片接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/stats` | 后台看板数据 |
| GET | `/api/images` | 分页列表，参数 `q`、`tag`、`category_id`、`page`、`limit` |
| GET | `/api/images/trash` | 回收站分页列表 |
| POST | `/api/images` | 多文件上传，表单字段 `files`、`tags`、`category_id`、`description` |
| POST | `/api/images/batch-delete` | 批量移入回收站，body `{ "ids": [1,2] }` |
| POST | `/api/images/batch-move` | 批量移动分类，body `{ "ids": [1], "category_id": 2 }` |
| GET | `/api/images/{id}` | 单张详情 |
| PATCH | `/api/images/{id}` | 更新文件名、描述、分类、标签 |
| DELETE | `/api/images/{id}` | 移入回收站（软删除） |
| POST | `/api/images/{id}/restore` | 从回收站恢复 |
| DELETE | `/api/images/{id}/purge` | 彻底删除（含磁盘文件） |
| POST | `/api/trash/empty` | 清空回收站 |
| GET | `/api/tags` | 全部标签及使用次数 |
| GET | `/api/feed` | 前台统一信息流，参数 `q`、`category_id`、`page`、`limit` |
| GET | `/api/media/original/{id}` | 原图 |
| GET | `/api/media/thumb/{id}` | 缩略图 |

## 广告图接口

广告图用于首页顶部轮播，独立于图片素材存储。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/banners` | 启用中的广告图，参数 `include_inactive=true` 返回全部 |
| POST | `/api/banners` | 批量上传广告图，表单字段 `files`、`title`、`link` |
| PATCH | `/api/banners/{id}` | 更新标题、链接、排序、启用状态 |
| DELETE | `/api/banners/{id}` | 删除广告图及文件 |
| GET | `/api/media/banner/{id}` | 广告图原图 |
| GET | `/api/media/banner-thumb/{id}` | 广告图缩略图 |

## 套图接口

套图是成组的多张图片，第一张上传的图片作为封面。套图成员不会单独出现在前台信息流中。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sets` | 套图列表 |
| POST | `/api/sets` | 创建套图，表单字段 `files`、`title`、`description`、`category_id`、`tags`，第一张为封面 |
| GET | `/api/sets/{id}` | 套图详情，含全部成员图片 |
| PATCH | `/api/sets/{id}` | 更新标题、描述、分类、标签或封面 |
| DELETE | `/api/sets/{id}` | 将套图及成员移入回收站 |
| POST | `/api/sets/{id}/restore` | 恢复套图及成员 |
| DELETE | `/api/sets/{id}/purge` | 彻底删除套图及全部成员文件 |
| GET | `/api/sets/trash` | 回收站中的套图列表 |

信息流条目结构：

```json
{
  "item_type": "image | set",
  "id": 1,
  "title": "夏日海边系列",
  "cover_image_id": 16,
  "category_id": 1,
  "category_name": "风景",
  "tags": ["旅行"],
  "image_count": 3,
  "width": 800,
  "height": 600,
  "created_at": "2026-09-18T12:00:00",
  "image": null
}
```

`item_type` 为 `image` 时 `image` 字段为该图片对象；为 `set` 时 `image` 为 null，改用 `cover_image_id` 读取封面。

## 分类接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 分类列表及素材数量、封面来源 |
| POST | `/api/categories` | 新增分类，body `{ "name", "description", "sort_order" }` |
| PATCH | `/api/categories/{id}` | 更新分类 |
| DELETE | `/api/categories/{id}` | 删除分类，原素材变为未分类 |
| POST | `/api/categories/{id}/cover` | 上传分类封面，表单字段 `file` |
| DELETE | `/api/categories/{id}/cover` | 移除分类封面，回退为自动封面 |
| GET | `/api/categories/{id}/cover` | 分类封面上传图原图 |
| GET | `/api/categories/{id}/cover-thumb` | 分类封面缩略图 |

## 前端路由与组件

路由：

| 路径 | 页面 |
|------|------|
| `/` | 首页（顶部广告轮播 + 三列分类卡 + 底部标签栏） |
| `/categories` | 分类页（左侧分类名称栏 + 右侧图片列表 + 搜索 + 底部标签栏） |
| `/set/:id` | 套图详情（沉浸封面 + 圆角内容层 + 三列成员网格） |
| `/admin/dashboard` | 后台数据看板 |
| `/admin/banners` | 广告图管理 |
| `/admin/categories` | 分类管理 |
| `/admin/upload` | 素材上传（单图 / 套图） |
| `/admin/assets` | 素材管理 |
| `/admin/trash` | 回收站 |

后台布局 `AdminLayout` 提供汉堡菜单侧边栏与顶栏标题「素材上传后台」，通过 `<router-view>` 渲染子页面。

组件：

- `TopBar` 接收 `showAdmin` / `showUpload`，触发 `search`、`upload`
- `SideNav` 接收 `categories`、`active`、`showUpload`
- `GalleryGrid` 接收 `items`、`selectedIds`、`selectable`，触发 `open`、`toggle-select`
- `Pagination` 接收 `page`、`total`、`limit`，触发 `change`
- `Lightbox` 接收当前图片与相邻切换回调，内部处理缩放、拖拽与键盘

## 错误约定

- 400：文件类型不支持、名称为空、分类不存在或名称重复
- 404：图片或分类不存在
- 413：单文件超过 20MB
- 500：写盘或缩略图生成失败

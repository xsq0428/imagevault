# Requirements Document

## Introduction

ImageVault 是一个单用户在线图库 Web 应用，提供图片上传、网格浏览、灯箱预览、标签分类、搜索与删除能力。系统包含 Vue 3 前端与 FastAPI 后端，无需登录。

## Glossary

- **Gallery**: 图片浏览主界面，由侧边分类栏、顶部搜索栏和双列网格组成
- **Lightbox**: 全屏图片预览层，支持缩放、拖拽和键盘切换
- **Tag**: 用户为图片设置的关键词，用于分类与筛选
- **Thumbnail**: 服务器生成的、最长边为 480 像素的 JPEG 预览图
- **Original**: 用户上传的未修改图片文件

## Requirements

### Requirement 1

**User Story:** AS 图库使用者, I want 上传本地图片, so that 图片可以被集中浏览和管理

#### Acceptance Criteria

1. WHEN 用户选择或拖入一个或多个图片文件, Gallery SHALL 将文件上传到服务器并保存为 Original
2. WHEN 上传的图片保存成功, 系统 SHALL 为该图片生成 Thumbnail 并记录文件名、尺寸与字节大小
3. IF 上传文件的 MIME 类型不在支持列表内, 系统 SHALL 拒绝该文件并返回 400 错误
4. IF 单个上传文件超过 20MB, 系统 SHALL 拒绝该文件并返回 413 错误
5. WHEN 上传请求包含标签字段, 系统 SHALL 为所有本次上传的图片关联这些标签

### Requirement 2

**User Story:** AS 图库使用者, I want 以双列网格浏览图片, so that 我可以在移动端快速浏览缩略图

#### Acceptance Criteria

1. 系统 SHALL 以两列等宽网格展示当前页图片的 Thumbnail
2. WHEN 视口宽度达到 760 像素, 系统 SHALL 将网格扩展为三列
3. WHEN 视口宽度达到 1040 像素, 系统 SHALL 将网格扩展为四列
4. WHEN 图库没有图片, 系统 SHALL 显示空状态提示与上传引导
5. WHILE 列表请求进行中, 系统 SHALL 显示加载状态

### Requirement 3

**User Story:** AS 图库使用者, I want 分页浏览图片, so that 大量图片不会一次性加载

#### Acceptance Criteria

1. 系统 SHALL 在每页固定返回 10 张图片
2. WHILE 总页数大于 1, 系统 SHALL 显示上一页、页码与下一页控件
3. WHEN 当前页码为第一页, 系统 SHALL 禁用上一页控件
4. WHEN 当前页码为最后一页, 系统 SHALL 禁用下一页控件
5. WHEN 切换页码, 系统 SHALL 回到页面顶部并加载对应页数据

### Requirement 4

**User Story:** AS 图库使用者, I want 在灯箱中查看原图, so that 我可以确认图片细节

#### Acceptance Criteria

1. WHEN 用户点击网格中的图片, 系统 SHALL 打开 Lightbox 并加载 Original
2. WHEN 用户在 Lightbox 中滚动滚轮, 系统 SHALL 在 0.5 倍到 5 倍之间调整图片缩放比例
3. WHILE 用户按住图片并移动指针, 系统 SHALL 按指针位移平移图片
4. WHEN 用户按下左方向键且存在上一张, 系统 SHALL 显示上一张图片
5. WHEN 用户按下右方向键且存在下一张, 系统 SHALL 显示下一张图片
6. WHEN 用户按下 Escape 键, 系统 SHALL 关闭 Lightbox

### Requirement 5

**User Story:** AS 图库使用者, I want 按标签分类和搜索, so that 我可以定位特定图片

#### Acceptance Criteria

1. 系统 SHALL 在侧边分类栏展示全部标签及其图片数量
2. WHEN 用户点击某个标签, 系统 SHALL 将网格筛选为该标签下的图片并重置到第一页
3. WHEN 用户在搜索框输入文件名关键词, 系统 SHALL 对文件名执行不区分大小写的模糊匹配
4. WHEN 搜索关键词与标签筛选同时存在, 系统 SHALL 返回同时满足两个条件的图片
5. WHILE 用户正在输入搜索词, 系统 SHALL 在停顿 320 毫秒后发起请求

### Requirement 6

**User Story:** AS 图库使用者, I want 删除不需要的图片, so that 图库保持整洁

#### Acceptance Criteria

1. WHEN 用户选择一张或多张图片, 系统 SHALL 显示已选数量与批量删除入口
2. WHEN 用户确认批量删除, 系统 SHALL 删除所选图片的数据库记录、Original 与 Thumbnail
3. WHEN 删除完成, 系统 SHALL 刷新当前列表并清除选择状态
4. IF 待删除的图片不存在, 系统 SHALL 返回 404 错误

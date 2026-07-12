# 极车 · 数据库设计文档（Django 4.2 + MySQL 8.0）

**文档版本**：V1.2  
**关联文档**：[二手摩托车获客小程序需求文档（极致可交付PRD｜Django+Vue+MySQL版）.md](./二手摩托车获客小程序需求文档（极致可交付PRD｜Django+Vue+MySQL版）.md)  
**数据库**：MySQL 8.0+，字符集 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`  
**设计原则**：逻辑删除、多租户 `shop_id` 隔离、状态枚举后端固定、外键保证一致性；**多端微信登录以 unionid 统一用户**

---

## 一、表关系总览

```
user ──┬── shop_application（入驻申请，1:N）
       ├── shop（商家，1:1，审核通过后）
       ├── favorite（收藏，1:N）
       ├── user_shop_visit（最近访问，1:N）
       ├── message_thread（咨询会话，1:N）
       └── auth_login_ticket（Web 扫码登录，1:N，临时）

shop ──┬── bike（车源，1:N）
       └── message_thread（咨询会话，1:N）

bike ──┬── bike_media（图片/视频，1:N）
       ├── message_thread（咨询会话，1:N）
       └── favorite（被收藏，1:N）

message_thread ── message_item（消息明细，1:N）

brand ── brand_model（车型字典，1:N）
```

**共计 12 张核心业务表**（不含 Django 内置扩展）。

---

## 二、全局枚举约定

| 枚举名 | 字段 | 取值 |
|---|---|---|
| shop_status | 用户/商家状态 | 0 普通用户 / 1 待审核 / 2 审核通过 / 3 审核驳回 / 4 违规封禁 |
| bike_status | 车辆状态 | 1 在售 / 2 已售 / 3 商家下架 / 4 违规下架 |
| is_deleted | 逻辑删除 | 0 正常 / 1 已删除 |
| thread_status | 会话状态 | 1 未读 / 2 已读未回复 / 3 已回复 |
| sender_type | 消息发送方 | 1 C 端用户 / 2 商家 / 3 系统通知 |
| shop_type | 入驻类型 | 1 个人商户 / 2 企业商户 |
| media_type | 媒体类型 | 1 封面 / 2 展示图 / 3 车况图 / 4 视频 |
| application_status | 申请审核状态 | 1 待审核 / 2 通过 / 3 驳回 |
| login_ticket_status | 扫码票据状态 | 0 待扫码 / 1 已扫码待确认 / 2 已确认 / 3 已过期 |
| login_platform | 登录平台 | mini_program / web |
| is_super_staff | 预置超管 | 0 否 / 1 是（不可被撤销） |

---

## 三、表结构详细设计

### 3.1 `user` — 用户表

扩展 Django 用户体系，承载**多端微信登录**与角色状态。同一微信用户在小程序与 Web 共用一条记录（通过 **unionid** 关联）。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| unionid | VARCHAR(64) | 否 | NULL | 微信 unionid，**多端统一主键（优先）**；绑定开放平台后必填 |
| mp_openid | VARCHAR(64) | 否 | NULL | 微信小程序 openid |
| web_openid | VARCHAR(64) | 否 | NULL | Web 扫码登录 openid（网站应用） |
| nickname | VARCHAR(64) | 否 | '' | 微信昵称 |
| phone | VARCHAR(11) | 否 | NULL | 手机号（咨询/contact 填写，非登录凭证） |
| avatar | VARCHAR(512) | 否 | NULL | 头像 URL |
| is_staff | TINYINT(1) | 是 | 0 | 是否平台管理员 |
| is_super_staff | TINYINT(1) | 是 | 0 | 是否预置超级管理员（不可前台注册、不可被撤销） |
| staff_granted_by | BIGINT UNSIGNED | 否 | NULL | 授予管理员权限的操作人 user.id |
| staff_granted_at | DATETIME | 否 | NULL | 授予管理员权限时间 |
| shop_status | TINYINT | 是 | 0 | 商家入驻状态，见枚举 |
| shop_id | BIGINT UNSIGNED | 否 | NULL | 关联商家 ID（审核通过后写入） |
| last_login_at | DATETIME | 否 | NULL | 最近登录时间 |
| last_login_platform | VARCHAR(16) | 否 | NULL | 最近登录平台：mini_program / web |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间（首次微信登录自动创建） |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除 |

**索引**：
- `UNIQUE uk_unionid (unionid)` — unionid 非空时唯一
- `UNIQUE uk_mp_openid (mp_openid)`
- `UNIQUE uk_web_openid (web_openid)`
- `INDEX idx_shop_status (shop_status)`
- `INDEX idx_shop_id (shop_id)`
- `INDEX idx_is_staff (is_staff)`

**多端账号规则**：
- 小程序首次登录：写 `mp_openid`；若有 unionid 则写入
- Web 扫码登录：写 `web_openid`；通过 unionid 合并到已有 user，否则新建
- **无账号密码字段**；C 端/商家不支持自助注册

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| 公共 | 微信扫码登录 | `/login` | Web 端登录；ticket 确认后写 token |
| 小程序 | 启动授权 | — | wx.login → mp_openid/unionid |
| C 端 | 个人中心 | `/profile` | 展示 nickname、shop_status |
| C 端 | 商家入驻申请 | `/apply-shop` | 读取 shop_status |
| C 端 | 我的咨询/收藏等 | `/messages`、`/favorites` 等 | 按 user_id 读写业务数据 |
| 商家后台 | 全部页面 | `/shop/*` | 鉴权：已登录 + shop_status=2 |
| 管理端 | 全部页面 | `/admin/*` | 鉴权：已登录 + is_staff=1 |
| 管理端 | 管理员管理 | `/admin/users` | 授予/撤销 is_staff |

---

### 3.2 `auth_login_ticket` — Web 微信扫码登录票据表

Web 端展示二维码，用户扫码确认后换取 token；与小程序共用 `user` 记录。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| ticket | VARCHAR(64) | 是 | - | 登录票据，**唯一** |
| status | TINYINT | 是 | 0 | 0 待扫码 / 1 已扫码待确认 / 2 已确认 / 3 已过期 |
| user_id | BIGINT UNSIGNED | 否 | NULL | 确认登录后绑定的 user.id |
| scan_openid | VARCHAR(64) | 否 | NULL | 扫码者 openid（确认时写入） |
| scan_unionid | VARCHAR(64) | 否 | NULL | 扫码者 unionid |
| redirect_path | VARCHAR(256) | 否 | NULL | 登录成功后 Web 跳转路径 |
| client_ip | VARCHAR(45) | 否 | NULL | 请求 IP |
| expires_at | DATETIME | 是 | - | 过期时间（建议 5 分钟） |
| confirmed_at | DATETIME | 否 | NULL | 确认时间 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：
- `UNIQUE uk_ticket (ticket)`
- `INDEX idx_status_expires (status, expires_at)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| Web 公共 | 微信扫码登录 | `/login` | 创建 ticket、轮询 status、确认后下发 token |
| 小程序 | 扫码确认页（待开发） | — | 扫描 Web 二维码后调用 confirm 接口 |

---

### 3.3 `shop` — 商家表（租户主体）

审核通过后创建的商家实体，**多租户隔离核心**，所有车源、会话均挂载 `shop_id`。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键，即 tenant shop_id |
| user_id | BIGINT UNSIGNED | 是 | - | 商家主账号，**唯一** |
| name | VARCHAR(64) | 是 | - | 商家名称 |
| shop_type | TINYINT | 是 | 1 | 1 个人 / 2 企业 |
| contact_name | VARCHAR(32) | 是 | - | 联系人姓名 |
| phone | VARCHAR(11) | 是 | - | 联系电话，**唯一** |
| address | VARCHAR(100) | 否 | '' | 经营地址 |
| main_models | VARCHAR(50) | 否 | '' | 主营车型 |
| description | VARCHAR(200) | 否 | '' | 商家简介 |
| avatar | VARCHAR(512) | 否 | NULL | 店铺头像 URL |
| wechat_qrcode | VARCHAR(512) | 是 | - | 微信二维码图片 URL |
| qualification_photo | VARCHAR(512) | 否 | NULL | 资质照片 URL |
| shop_status | TINYINT | 是 | 2 | 2 正常 / 4 封禁 |
| approved_at | DATETIME | 否 | NULL | 审核通过时间 |
| banned_at | DATETIME | 否 | NULL | 封禁时间 |
| ban_reason | VARCHAR(200) | 否 | NULL | 封禁原因 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除 |

**索引**：
- `UNIQUE uk_user_id (user_id)`
- `UNIQUE uk_phone (phone)`
- `INDEX idx_shop_status (shop_status)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 商家主页 | `/shop/:id` | 展示 name、avatar、address、wechat_qrcode、简介 |
| C 端 | 商品详情 | `/bike/:id` | 侧边/底部展示所属 shop 信息与二维码 |
| C 端 | 首页 | `/` | 「最近访问商家」展示 shop.name |
| 商家后台 | 商家资料 | `/shop/profile` | 编辑 name、contact、address、qrcode 等 |
| 商家后台 | 工作台 | `/shop/dashboard` | 统计本 shop 数据 |
| 管理端 | 商户管理 | `/admin/shops` | 列表、封禁/解封 |
| 管理端 | 车源管控 | `/admin/bikes` | 展示 shop_name（JOIN） |

---

### 3.4 `shop_application` — 商家入驻申请表

每次入驻/重新提交产生记录，供管理员审核。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| user_id | BIGINT UNSIGNED | 是 | - | 申请人 |
| shop_type | TINYINT | 是 | - | 1 个人 / 2 企业 |
| contact_name | VARCHAR(32) | 是 | - | 联系人 |
| phone | VARCHAR(11) | 是 | - | 联系电话 |
| address | VARCHAR(100) | 否 | '' | 经营地址 |
| main_models | VARCHAR(50) | 否 | '' | 主营车型 |
| description | VARCHAR(200) | 否 | '' | 入驻说明 |
| wechat_qrcode | VARCHAR(512) | 是 | - | 微信二维码 URL |
| qualification_photo | VARCHAR(512) | 否 | NULL | 资质照片 |
| application_status | TINYINT | 是 | 1 | 1 待审 / 2 通过 / 3 驳回 |
| reject_reason | VARCHAR(200) | 否 | NULL | 驳回原因 |
| audited_by | BIGINT UNSIGNED | 否 | NULL | 审核管理员 user.id |
| audited_at | DATETIME | 否 | NULL | 审核时间 |
| applied_at | DATETIME | 是 | CURRENT_TIMESTAMP | 申请时间 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除 |

**索引**：
- `INDEX idx_user_id (user_id)`
- `INDEX idx_application_status (application_status)`
- `INDEX idx_applied_at (applied_at DESC)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 商家入驻申请 | `/apply-shop` | 提交/查看申请、展示驳回原因 |
| C 端 | 个人中心 | `/profile` | 根据 user.shop_status 展示入驻状态引导 |
| 管理端 | 商家审核 | `/admin/audit` | 列表、通过/驳回、填写 reject_reason |

---

### 3.5 `brand` — 车辆品牌字典表

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | INT UNSIGNED | 是 | AUTO | 主键 |
| name | VARCHAR(32) | 是 | - | 品牌名称，**唯一** |
| sort_order | INT | 是 | 0 | 排序权重 |
| is_enabled | TINYINT(1) | 是 | 1 | 是否启用 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：`UNIQUE uk_name (name)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| 商家后台 | 发布/编辑车源 | `/shop/bikes/new`、`/shop/bikes/:id/edit` | 品牌下拉选项 |

---

### 3.6 `brand_model` — 车型字典表

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | INT UNSIGNED | 是 | AUTO | 主键 |
| brand_id | INT UNSIGNED | 是 | - | 关联 brand.id |
| name | VARCHAR(64) | 是 | - | 车型名称 |
| is_enabled | TINYINT(1) | 是 | 1 | 是否启用 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：
- `INDEX idx_brand_id (brand_id)`
- `UNIQUE uk_brand_model (brand_id, name)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| 商家后台 | 发布/编辑车源 | `/shop/bikes/new`、`/shop/bikes/:id/edit` | 选择品牌后加载车型列表 |

---

### 3.7 `bike` — 机车/商品表

多租户核心商品表，C 端仅在同 `shop_id` 域内可见。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| shop_id | BIGINT UNSIGNED | 是 | - | 所属商家（租户 ID） |
| brand_id | INT UNSIGNED | 否 | NULL | 品牌 ID（冗余 brand 名便于检索） |
| brand | VARCHAR(32) | 是 | - | 品牌名称（冗余展示） |
| model | VARCHAR(64) | 是 | - | 车型 |
| year | SMALLINT | 是 | - | 上牌年份 |
| register_date | DATE | 否 | NULL | 上牌日期（PRD 要求，精确到日） |
| displacement | VARCHAR(16) | 是 | - | 排量，如 400cc |
| mileage | INT UNSIGNED | 是 | 0 | 行驶里程 km |
| transfer_count | TINYINT UNSIGNED | 是 | 0 | 过户次数 0–99 |
| price | DECIMAL(12,2) | 是 | - | 售价（元） |
| can_transfer | TINYINT(1) | 是 | 1 | 是否可过户 |
| negotiable | TINYINT(1) | 是 | 1 | 是否可议价 |
| engine_status | VARCHAR(500) | 是 | - | 发动机状态说明 |
| suspension_status | VARCHAR(500) | 是 | - | 减震状态 |
| brake_status | VARCHAR(500) | 是 | - | 刹车状态 |
| electrical_status | VARCHAR(500) | 是 | - | 电控状态 |
| frame_status | VARCHAR(500) | 是 | - | 车架状态 |
| modification | VARCHAR(500) | 是 | - | 改装明细 |
| defects | VARCHAR(500) | 是 | - | 瑕疵说明 |
| maintenance | VARCHAR(500) | 是 | - | 维保/整备记录 |
| delivery_method | VARCHAR(64) | 否 | '' | 交付方式，如「自提/物流」 |
| fee_note | VARCHAR(200) | 否 | '' | 费用说明 |
| after_sale | VARCHAR(200) | 否 | '' | 售后说明 |
| cover_image | VARCHAR(512) | 是 | - | 封面图 URL（冗余，取自 media 首图） |
| bike_status | TINYINT | 是 | 1 | 1 在售 / 2 已售 / 3 下架 / 4 违规下架 |
| view_count | INT UNSIGNED | 是 | 0 | 浏览次数 |
| published_at | DATETIME | 否 | NULL | 首次上架时间（排序用） |
| off_shelf_at | DATETIME | 否 | NULL | 下架时间 |
| force_off_reason | VARCHAR(200) | 否 | NULL | 违规下架原因（管理员填写） |
| force_off_by | BIGINT UNSIGNED | 否 | NULL | 违规操作管理员 ID |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除；收藏列表展示「商家已删除」 |

**索引**：
- `INDEX idx_shop_status_published (shop_id, bike_status, published_at DESC)` — 商家域列表排序
- `INDEX idx_shop_deleted (shop_id, is_deleted)`
- `INDEX idx_price (price)`
- `INDEX idx_year (year)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 商品详情 | `/bike/:id` | 全字段展示、收藏、留言、分享 |
| C 端 | 商家主页 | `/shop/:id` | 租户内车源列表、筛选排序 |
| C 端 | 我的收藏 | `/favorites` | JOIN 展示收藏商品；is_deleted=1 显示失效 |
| 商家后台 | 车源列表 | `/shop/bikes` | CRUD、下架、分享链接、排序 |
| 商家后台 | 发布/编辑 | `/shop/bikes/new`、`/shop/bikes/:id/edit` | 写入/更新 |
| 商家后台 | 工作台 | `/shop/dashboard` | 统计在售/已售/浏览量 |
| 管理端 | 车源管控 | `/admin/bikes` | 全平台列表、强制下架/恢复 |
| 管理端 | 留言查看 | `/admin/messages` | 展示 bike_info（JOIN） |

---

### 3.8 `bike_media` — 商品媒体表

统一管理封面、展示图、车况图、视频。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| bike_id | BIGINT UNSIGNED | 是 | - | 关联 bike.id |
| shop_id | BIGINT UNSIGNED | 是 | - | 冗余租户 ID，便于权限校验 |
| media_type | TINYINT | 是 | - | 1 封面 / 2 展示图 / 3 车况图 / 4 视频 |
| url | VARCHAR(512) | 是 | - | 媒体文件 URL |
| sort_order | INT | 是 | 0 | 同类型内排序 |
| duration | INT | 否 | NULL | 视频时长（秒），≤60 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除 |

**索引**：
- `INDEX idx_bike_type_sort (bike_id, media_type, sort_order)`
- `INDEX idx_shop_id (shop_id)`

**约束**：展示图（type=2）每车 3–20 张；视频（type=4）每车最多 1 条。

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 商品详情 | `/bike/:id` | 轮播图、车况实拍图、视频 |
| C 端 | 商家主页 | `/shop/:id` | 列表卡片 cover_image |
| 商家后台 | 发布/编辑 | `/shop/bikes/new`、`/shop/bikes/:id/edit` | 上传/删除图片视频 |

---

### 3.9 `message_thread` — 咨询会话表

一个用户 + 一个商家 + 一台商品 = 一条会话（可多轮 message_item）。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| shop_id | BIGINT UNSIGNED | 是 | - | 商家 ID |
| bike_id | BIGINT UNSIGNED | 是 | - | 商品 ID |
| user_id | BIGINT UNSIGNED | 是 | - | C 端用户 ID |
| contact_phone | VARCHAR(11) | 否 | NULL | 首条咨询联系电话（选填） |
| thread_status | TINYINT | 是 | 1 | 1 未读 / 2 已读未回复 / 3 已回复 |
| unread_count_user | INT UNSIGNED | 是 | 0 | 用户侧未读数 |
| unread_count_shop | INT UNSIGNED | 是 | 0 | 商家侧未读数 |
| last_message_at | DATETIME | 否 | NULL | 最后一条消息时间 |
| last_message_preview | VARCHAR(100) | 否 | NULL | 列表预览文案 |
| user_read_at | DATETIME | 否 | NULL | 用户最后已读时间 |
| shop_read_at | DATETIME | 否 | NULL | 商家最后已读时间 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除（业务上不可删，仅兜底） |

**索引**：
- `UNIQUE uk_user_bike (user_id, bike_id)` — 同用户同商品唯一会话
- `INDEX idx_shop_status (shop_id, thread_status, last_message_at DESC)`
- `INDEX idx_user (user_id, last_message_at DESC)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 我的咨询 | `/messages` | 会话列表、未读角标 |
| C 端 | 咨询对话 | `/messages/:threadId` | 会话详情头部信息 |
| C 端 | 商品详情 | `/bike/:id` | 发起咨询时 create/find |
| 商家后台 | 留言管理 | `/shop/messages` | 本店会话列表、未读角标 |
| 商家后台 | 咨询对话 | `/shop/messages/:threadId` | 商家回复 |
| 商家后台 | 工作台 | `/shop/dashboard` | 未读留言统计 |
| 管理端 | 留言查看 | `/admin/messages` | 全平台只读列表 |

---

### 3.10 `message_item` — 会话消息明细表

多轮对话消息，永久留存。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| thread_id | BIGINT UNSIGNED | 是 | - | 关联 message_thread.id |
| shop_id | BIGINT UNSIGNED | 是 | - | 冗余租户 ID |
| sender_type | TINYINT | 是 | - | 1 用户 / 2 商家 / 3 系统 |
| sender_id | BIGINT UNSIGNED | 是 | - | 发送者 user.id |
| content | VARCHAR(500) | 是 | - | 消息内容 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 发送时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 逻辑删除 |

**索引**：
- `INDEX idx_thread_created (thread_id, created_at ASC)`
- `INDEX idx_shop_id (shop_id)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 咨询对话 | `/messages/:threadId` | 气泡列表、发送消息 |
| 商家后台 | 咨询对话 | `/shop/messages/:threadId` | 商家回复 |
| 管理端 | 留言查看 | `/admin/messages` | 只读展示多轮记录 |

---

### 3.11 `favorite` — 用户收藏表

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| user_id | BIGINT UNSIGNED | 是 | - | 收藏用户 |
| bike_id | BIGINT UNSIGNED | 是 | - | 收藏商品 |
| shop_id | BIGINT UNSIGNED | 是 | - | 冗余 shop_id，便于租户校验 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 收藏时间 |
| is_deleted | TINYINT(1) | 是 | 0 | 用户删除收藏时置 1（或物理删，推荐逻辑删） |

**索引**：
- `UNIQUE uk_user_bike (user_id, bike_id)`
- `INDEX idx_user_created (user_id, created_at DESC)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 我的收藏 | `/favorites` | 列表、删除收藏 |
| C 端 | 商品详情 | `/bike/:id` | 收藏/取消收藏 |
| C 端 | 商家主页 | `/shop/:id` | 卡片上收藏按钮 |

**说明**：列表接口 JOIN `bike`，若 `bike.is_deleted=1` 则前端展示「商家已删除」，禁止进入详情。

---

### 3.12 `user_shop_visit` — 用户最近访问商家表

记录 C 端通过分享链接进入的商家，供首页「最近访问」展示（可替代纯 localStorage）。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| id | BIGINT UNSIGNED | 是 | AUTO | 主键 |
| user_id | BIGINT UNSIGNED | 是 | - | 用户 ID |
| shop_id | BIGINT UNSIGNED | 是 | - | 商家 ID |
| visit_count | INT UNSIGNED | 是 | 1 | 访问次数 |
| last_visited_at | DATETIME | 是 | CURRENT_TIMESTAMP | 最近访问时间 |
| created_at | DATETIME | 是 | CURRENT_TIMESTAMP | 首次访问时间 |
| updated_at | DATETIME | 是 | ON UPDATE | 更新时间 |

**索引**：
- `UNIQUE uk_user_shop (user_id, shop_id)`
- `INDEX idx_user_last (user_id, last_visited_at DESC)`

**关联页面**：

| 端 | 页面 | 路由 | 用途 |
|---|---|---|---|
| C 端 | 首页 | `/` | 最近访问商家列表 |
| C 端 | 商家主页 | `/shop/:id` | 进入时 upsert 访问记录 |
| C 端 | 商品详情 | `/bike/:id` | 进入时 upsert（写入 shop_id） |

---

## 四、页面 ↔ 数据表对照矩阵

| 页面（路由） | 主要读表 | 主要写表 |
|---|---|---|
| **微信登录** `/login` | auth_login_ticket | auth_login_ticket, user |
| C 端首页 `/` | user_shop_visit, shop | user_shop_visit |
| 商品详情 `/bike/:id` | bike, bike_media, shop | message_thread, message_item, favorite, user_shop_visit |
| 商家主页 `/shop/:id` | shop, bike | user_shop_visit |
| 我的收藏 `/favorites` | favorite, bike | favorite |
| 我的咨询 `/messages` | message_thread, bike | - |
| 咨询对话 `/messages/:id` | message_thread, message_item | message_item, message_thread |
| 个人中心 `/profile` | user | - |
| 商家入驻 `/apply-shop` | shop_application, user | shop_application, user |
| 商家工作台 `/shop/dashboard` | bike, message_thread | - |
| 商家车源 `/shop/bikes/*` | brand, brand_model, bike, bike_media | bike, bike_media |
| 商家留言 `/shop/messages` | message_thread, message_item | message_item, message_thread |
| 商家资料 `/shop/profile` | shop | shop |
| 管理首页 `/admin/dashboard` | shop, bike, shop_application, message_thread | - |
| 商家审核 `/admin/audit` | shop_application, user | shop_application, shop, user |
| 商户管理 `/admin/shops` | shop, user | shop, user |
| 车源管控 `/admin/bikes` | bike, shop | bike |
| 留言查看 `/admin/messages` | message_thread, message_item, bike, user | - |
| **管理员管理** `/admin/users` | user | user（is_staff 字段） |

---

## 五、关键业务规则（数据库层需配合应用层）

1. **多租户隔离**：C 端查询 `bike`、`message_thread` 必须带 `shop_id`；商家仅允许 `shop_id = 当前用户.shop_id`。
2. **列表排序**：商家域 `bike` 列表按 `bike_status ASC（1 优先）, published_at DESC` 排序。
3. **违规恢复**：仅管理员可将 `bike_status` 从 4 改回 1；商家不可更新 status=4 的记录为在售。
4. **逻辑删除**：`bike.is_deleted=1` 后 C 端不可见；`favorite` 保留，前端展示失效态。
5. **会话唯一**：同一 `user_id + bike_id` 仅一条 `message_thread`；新咨询 append `message_item`。
6. **未读计数**：发送 `message_item` 时更新 `message_thread.unread_count_*` 与 `thread_status`；进入对话页更新 `*_read_at` 并清零对应未读。
7. **入驻审核通过**：写入 `shop`、更新 `user.shop_status=2` 与 `user.shop_id`、更新 `shop_application.application_status=2`。
8. **封禁商家**：`user.shop_status=4`、`shop.shop_status=4`，商家后台接口拒绝访问。
9. **多端登录**：小程序与 Web 通过 unionid 映射同一 `user_id`；收藏/咨询/访问记录按 user_id 共享。
10. **管理员授权**：仅 `is_staff=1` 用户可授予他人 `is_staff`；`is_super_staff=1` 不可被撤销；不支持前台注册管理员。

---

## 六、Django Model 命名建议

| MySQL 表名 | Django Model 建议 |
|---|---|
| user | `accounts.User` |
| auth_login_ticket | `accounts.AuthLoginTicket` |
| shop | `shops.Shop` |
| shop_application | `shops.ShopApplication` |
| brand | `catalog.Brand` |
| brand_model | `catalog.BrandModel` |
| bike | `bikes.Bike` |
| bike_media | `bikes.BikeMedia` |
| message_thread | `messages.MessageThread` |
| message_item | `messages.MessageItem` |
| favorite | `favorites.Favorite` |
| user_shop_visit | `shops.UserShopVisit` |

---

## 七、版本记录

| 版本 | 说明 |
|---|---|
| V1.1 | 对齐 PRD V1.1：多租户、多轮留言、收藏失效、published_at 排序、违规下架权限 |
| V1.2 | 多端微信登录：user 字段拆分 mp/web openid、unionid；新增 auth_login_ticket；管理员授权字段 |

> 本文档可直接用于 MySQL 建表、Django Model 编写与接口字段对齐。若后续增加订阅消息模板、分享短链等，可扩展 `notification_log`、`share_link` 等辅助表，不影响当前核心表结构。

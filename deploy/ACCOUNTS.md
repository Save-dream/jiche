# 初始登录账号（账号密码登录）

执行命令创建/重置：

```bash
cd /home/jiche/jiche-backend
source .venv/bin/activate   # 或用你的 Python 虚拟环境
python manage.py create_init_accounts --reset-password
```

| 账号 | 密码 | 角色 | 说明 |
|------|------|------|------|
| `admin` | `Jiche@Admin2026` | 平台管理员 | 可进管理中心 |
| `shop` | `Jiche@Shop2026` | 已入驻商家 | 可进商家后台，店铺可自行修改 |
| `user` | `Jiche@User2026` | 普通用户 | C 端浏览 / 收藏 / 咨询 |

登录地址：`http://你的域名或IP/login`  
接口：`POST /api/auth/login/`，body：`{"username":"admin","password":"Jiche@Admin2026"}`

> 微信扫码登录暂未启用。上线正式微信登录前请修改默认密码。

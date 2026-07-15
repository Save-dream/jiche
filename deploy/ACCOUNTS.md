# 初始登录账号（账号密码登录）

执行命令创建/重置预置账号：

```bash
cd /home/jiche/jiche-backend
# Docker：
# sudo docker compose exec backend python manage.py create_init_accounts --reset-password
source .venv/bin/activate
python manage.py create_init_accounts --reset-password
```

| 账号 | 密码 | 角色 | 说明 |
|------|------|------|------|
| `admin` | `Jiche@Admin2026` | 平台管理员（预置） | **不可封禁、不可删除** |
| `shop` | `Jiche@Shop2026` | 已入驻商家 | 可进商家后台 |
| `user` | `Jiche@User2026` | 普通用户 | 也可在登录页自助注册新用户 |

## 普通用户注册（测试期 / 微信未接通）

- 页面：`/login` →「去注册」
- 接口：`POST /api/auth/register/`  
  body：`{"username","password","nickname?","phone?"}`  
  成功后直接返回 token（等同授权登录建号）

## 用户管理规则

| 对象 | 封禁 | 删除 | 授予管理员 |
|------|------|------|------------|
| 普通用户 | ✅（封禁后无法登录） | ✅（逻辑删除，需理由） | ✅ |
| 平台管理员（含授权） | ❌ | ❌ | — |
| 预置超管 | ❌ | ❌ | 不可撤销 |

登录：`POST /api/auth/login/`  
封禁后登录提示：「账号已被封禁，无法登录」

> 微信扫码登录暂未启用。正式接通微信后，「注册」将由微信授权替代。

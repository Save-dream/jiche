#!/usr/bin/env python3
"""端到端 API 冒烟自测（工程师角色验收脚本）"""
import json
import sys
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:8000/api'
PASS = []
FAIL = []
WARN = []


def req(method, path, token=None, data=None):
    url = f'{BASE}{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {'msg': raw}
        return e.code, payload


def ok(name, cond, detail=''):
    if cond:
        PASS.append(name)
        print(f'  ✓ {name}')
    else:
        FAIL.append(f'{name}: {detail}')
        print(f'  ✗ {name} — {detail}')


def warn(name, detail=''):
    WARN.append(f'{name}: {detail}')
    print(f'  ! {name} — {detail}')


def login(role):
    code, res = req('POST', '/auth/dev/login/', data={'role': role})
    if code != 200 or res.get('code') != 200:
        raise RuntimeError(f'login {role} failed: {code} {res}')
    return res['data']['token'], res['data']['user']


def main():
    print('\n=== 工程师自测：认证模块 ===')
    user_token, user = login('user')
    shop_token, shop_user = login('shop')
    admin_token, admin = login('admin')
    pending_token, pending = login('pending')

    code, me = req('GET', '/auth/me/', token=user_token)
    ok('普通用户 /auth/me/', code == 200 and me['data']['nickname'] == '普通用户')

    code, me = req('GET', '/auth/me/', token=shop_token)
    ok('商家 /auth/me/ shop_status=2', code == 200 and me['data'].get('shop_status') == 2)

    code, me = req('GET', '/auth/me/', token=admin_token)
    ok('管理员 /auth/me/ is_staff', code == 200 and me['data'].get('is_staff') is True)

    print('\n=== 普通用户：浏览 / 收藏 / 留言 / 访问 ===')
    shop_id = shop_user.get('shop_id') or 1

    code, shop_detail = req('GET', f'/shops/{shop_id}/')
    ok('C端商家详情', code == 200 and shop_detail['data']['shop']['name'])
    bikes = shop_detail['data'].get('bikes') or []
    if not bikes:
        warn('商家暂无车源', '需商家先发布车源才能测收藏/留言')

    bike_id = bikes[0]['id'] if bikes else None

    if bike_id:
        code, bike = req('GET', f'/bikes/{bike_id}/?shop_id={shop_id}')
        ok('C端车源详情（带 shop_id）', code == 200 and bike['data']['id'] == bike_id)

        code, _ = req('GET', f'/bikes/{bike_id}/')
        ok('C端车源详情（无 shop_id 应拒绝）', code == 403 or (code == 200 and _.get('code') == 403))

        code, fav = req('POST', '/favorites/', token=user_token, data={'bike_id': bike_id})
        ok('添加收藏', code == 200 and fav['code'] == 200)

        code, favs = req('GET', '/favorites/', token=user_token)
        ok('收藏列表', code == 200 and any(b['id'] == bike_id for b in favs['data']['list']))

        code, thread = req('POST', '/message-threads/', token=user_token, data={
            'shop_id': shop_id,
            'bike_id': bike_id,
            'content': '自测留言：这辆车还在吗？',
        })
        ok('创建留言会话', code == 200 and thread['data'].get('id'))
        thread_id = thread['data']['id'] if thread.get('code') == 200 else None

        if thread_id:
            code, send = req('POST', f'/message-threads/{thread_id}/messages/', token=user_token, data={
                'content': '自测追问：可以试驾吗？',
                'sender_type': 1,
            })
            ok('用户追留言', code == 200)

            code, threads = req('GET', '/message-threads/', token=user_token)
            ok('用户留言列表', code == 200 and threads['data']['total'] >= 1)

    code, visit = req('POST', '/visits/', token=user_token, data={'shop_id': shop_id})
    ok('记录访问商家', code == 200 and visit['data'].get('recorded'))

    code, visits = req('GET', '/visits/', token=user_token)
    ok('最近访问列表', code == 200 and visits['data']['total'] >= 1)

    print('\n=== 普通用户：入驻申请（待审账号应不可重复提交）===')
    code, app = req('GET', '/applications/my/', token=pending_token)
    ok('待审用户查看自己的申请', code == 200)

    code, dup = req('POST', '/applications/', token=pending_token, data={
        'name': '重复车行', 'shop_type': 1, 'contact_name': '重复', 'phone': '13600000002',
        'address': '广州', 'main_models': '本田', 'description': '重复提交测试',
        'wechat_qrcode': '/media/test.jpg',
    })
    ok('待审不可重复提交', dup.get('code') != 200 or code != 200)

    print('\n=== 商家：车源 CRUD / 资料 / 留言回复 ===')
    code, brands = req('GET', '/brands/')
    ok('品牌字典', code == 200 and len(brands['data']) >= 1)
    brand = brands['data'][0]

    code, models = req('GET', f'/brands/{brand["id"]}/models/')
    ok('车型字典', code == 200 and len(models['data']) >= 1)

    code, created = req('POST', '/shop/bikes/', token=shop_token, data={
        'brand_id': brand['id'],
        'brand': brand['name'],
        'model': models['data'][0],
        'year': 2022,
        'displacement': '400cc',
        'mileage': 8000,
        'transfer_count': 0,
        'price': 35000,
        'can_transfer': True,
        'negotiable': True,
        'engine_status': '正常',
        'suspension_status': '正常',
        'brake_status': '正常',
        'electrical_status': '正常',
        'frame_status': '正常',
        'modification': '无',
        'defects': '无',
        'maintenance': '定期保养',
        'delivery_method': '自提',
        'cover_image': 'https://placehold.co/800x600?text=bike1',
        'images': [
            'https://placehold.co/800x600?text=bike1',
            'https://placehold.co/800x600?text=bike2',
            'https://placehold.co/800x600?text=bike3',
        ],
        'condition_images': [],
    })
    ok('商家发布车源', code == 200 and created['data'].get('id'))
    new_bike_id = created['data']['id'] if created.get('code') == 200 else bike_id

    if new_bike_id:
        code, detail = req('GET', f'/shop/bikes/{new_bike_id}/', token=shop_token)
        ok('商家获取车源详情', code == 200)

        code, off = req('POST', f'/shop/bikes/{new_bike_id}/off-shelf/', token=shop_token)
        ok('商家下架', code == 200 and off['data']['bike_status'] == 3)

        code, on = req('POST', f'/shop/bikes/{new_bike_id}/on-shelf/', token=shop_token)
        ok('商家重新上架', code == 200 and on['data']['bike_status'] == 1)

    code, profile = req('GET', '/shop/profile/', token=shop_token)
    ok('商家资料读取', code == 200 and profile['data']['name'])

    code, updated = req('PUT', '/shop/profile/', token=shop_token, data={
        'description': '自测更新简介',
    })
    ok('商家资料更新', code == 200 and '自测更新简介' in updated['data']['description'])

    code, stats = req('GET', '/shop/stats/', token=shop_token)
    ok('商家统计', code == 200 and 'on_sale' in stats['data'])

    code, shop_threads = req('GET', '/shop/message-threads/', token=shop_token)
    ok('商家留言列表', code == 200)
    if shop_threads['data']['list']:
        tid = shop_threads['data']['list'][0]['id']
        code, reply = req('POST', f'/message-threads/{tid}/messages/', token=shop_token, data={
            'content': '商家回复：欢迎来看车',
            'sender_type': 2,
        })
        ok('商家回复留言', code == 200)

    print('\n=== 平台管理员：审核 / 管控 ===')
    code, apps = req('GET', '/admin/applications/', token=admin_token)
    ok('待审申请列表', code == 200)

    code, shops = req('GET', '/admin/shops/', token=admin_token)
    ok('商户列表', code == 200 and shops['data']['total'] >= 1)
    sid = shops['data']['list'][0]['id']

    code, all_bikes = req('GET', '/admin/bikes/', token=admin_token)
    ok('全平台车源列表', code == 200)
    test_bike = all_bikes['data']['list'][0]['id'] if all_bikes['data']['list'] else new_bike_id

    if test_bike:
        code, force = req('POST', f'/admin/bikes/{test_bike}/force-off-shelf/', token=admin_token, data={'reason': '自测违规'})
        ok('管理员强制下架', code == 200 and force['data']['bike_status'] == 4)

        code, restore = req('POST', f'/admin/bikes/{test_bike}/restore/', token=admin_token)
        ok('管理员恢复上架', code == 200 and restore['data']['bike_status'] == 1)

        # 商家不可编辑违规下架车辆
        code, edit = req('PUT', f'/shop/bikes/{test_bike}/', token=shop_token, data={
            'brand': brand['name'], 'model': models['data'][0], 'year': 2022,
            'displacement': '400cc', 'price': 36000,
            'cover_image': 'https://placehold.co/800x600?text=bike1',
            'images': ['https://placehold.co/800x600?text=bike1'] * 3,
        })
        # 先强制下架再测编辑
        req('POST', f'/admin/bikes/{test_bike}/force-off-shelf/', token=admin_token, data={'reason': 'x'})
        code, edit = req('PUT', f'/shop/bikes/{test_bike}/', token=shop_token, data={
            'brand': brand['name'], 'model': models['data'][0], 'year': 2022,
            'displacement': '400cc', 'price': 36000,
            'engine_status': '正常', 'suspension_status': '正常', 'brake_status': '正常',
            'electrical_status': '正常', 'frame_status': '正常',
            'modification': '无', 'defects': '无', 'maintenance': '正常',
            'cover_image': 'https://placehold.co/800x600?text=bike1',
            'images': ['https://placehold.co/800x600?text=bike1'] * 3,
        })
        ok('违规下架车辆商家不可编辑', edit.get('code') != 200 or code != 200)
        req('POST', f'/admin/bikes/{test_bike}/restore/', token=admin_token)

    code, users = req('GET', '/admin/users/', token=admin_token)
    ok('用户管理列表', code == 200 and users['data']['total'] >= 1)

    code, admin_stats = req('GET', '/admin/stats/', token=admin_token)
    ok('平台统计', code == 200 and 'total_shops' in admin_stats['data'])

    code, msgs = req('GET', '/admin/message-threads/', token=admin_token)
    ok('管理端留言监管', code == 200)

  # 权限隔离
    print('\n=== 权限隔离 ===')
    code, _ = req('GET', '/admin/shops/', token=user_token)
    ok('普通用户不可访问管理端', _.get('code') == 403 or code == 403)

    code, _ = req('GET', '/shop/bikes/', token=user_token)
    ok('普通用户不可访问商家后台', _.get('code') == 403 or code == 403)

    print('\n' + '=' * 50)
    print(f'通过: {len(PASS)}  失败: {len(FAIL)}  警告: {len(WARN)}')
    if FAIL:
        print('\n失败项:')
        for f in FAIL:
            print(f'  - {f}')
    if WARN:
        print('\n警告项:')
        for w in WARN:
            print(f'  - {w}')
    return 0 if not FAIL else 1


if __name__ == '__main__':
    sys.exit(main())

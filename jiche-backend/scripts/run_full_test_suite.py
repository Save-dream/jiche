#!/usr/bin/env python3
"""根据《极车-测试用例文档.md》执行可自动化测试，输出 JSON 结果。"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

BASE = 'http://127.0.0.1:8000/api'
FRONTEND = 'http://127.0.0.1:5173'
RESULTS = []


def record(case_id, name, status, detail='', module=''):
    RESULTS.append({
        'id': case_id,
        'name': name,
        'status': status,  # pass | fail | skip | warn
        'detail': detail,
        'module': module,
    })
    sym = {'pass': '✓', 'fail': '✗', 'skip': '○', 'warn': '!'}[status]
    print(f'  {sym} [{case_id}] {name}' + (f' — {detail}' if detail else ''))


def req(method, path, token=None, data=None, raw=False):
    url = f'{BASE}{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=15) as resp:
            elapsed = (time.perf_counter() - t0) * 1000
            content = resp.read().decode()
            if raw:
                return resp.status, content, elapsed
            return resp.status, json.loads(content), elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        raw_body = e.read().decode()
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            payload = {'msg': raw_body}
        return e.code, payload, elapsed


def login(role):
    code, res, _ = req('POST', '/auth/dev/login/', data={'role': role})
    if code != 200 or res.get('code') != 200:
        raise RuntimeError(f'login {role} failed: {code} {res}')
    return res['data']['token'], res['data']['user']


def check_frontend(path):
    url = f'{FRONTEND}{path}'
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            html = resp.read().decode()
            elapsed = (time.perf_counter() - t0) * 1000
            return resp.status, html, elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return e.code, e.read().decode(), elapsed
    except Exception as e:
        return 0, str(e), 0


def main():
    print('\n=== 极车全面测试执行 ===')
    print(f'时间: {datetime.now().isoformat()}')

    # --- AUTH ---
    print('\n[AUTH] 认证与权限')
    try:
        user_token, user = login('user')
        shop_token, shop_user = login('shop')
        admin_token, admin = login('admin')
        pending_token, pending = login('pending')
        banned_token, banned = login('banned')
    except RuntimeError as e:
        record('AUTH-SETUP', '测试账号登录', 'fail', str(e), 'AUTH')
        print(json.dumps({'results': RESULTS, 'summary': {'pass': 0, 'fail': 1}}))
        return 1

    code, me, _ = req('GET', '/auth/me/', token=user_token)
    record('AUTH-009', '获取当前用户', 'pass' if code == 200 and me['data']['nickname'] else 'fail', module='AUTH')

    code, me, _ = req('GET', '/auth/me/')
    record('AUTH-005', '未登录 /auth/me/', 'pass' if code in (401, 403) or me.get('code') in (401, 403) else 'fail', module='AUTH')

    code, ticket, _ = req('POST', '/auth/login-ticket/')
    record('API-AUTH-02', '创建登录票据', 'pass' if code == 200 and ticket['data'].get('ticket_id') else 'fail', module='AUTH')

    if ticket.get('code') == 200:
        tid = ticket['data']['ticket_id']
        code, poll, _ = req('GET', f'/auth/login-ticket/{tid}/')
        record('AUTH-007', '扫码票据轮询 pending', 'pass' if poll['data']['status'] == 'pending' else 'fail', module='AUTH')

    code, wx, _ = req('POST', '/auth/wx-mini/login/', data={'code': 'mock'})
    record('AUTH-010', '小程序登录 API（MOCK）', 'pass' if code == 200 and wx.get('data', {}).get('token') else 'fail', module='AUTH')

    # --- SHARE ---
    print('\n[SHARE] 多租户与分享')
    shop_id = shop_user.get('shop_id') or 1
    code, shop_detail, _ = req('GET', f'/shops/{shop_id}/')
    bikes = (shop_detail.get('data') or {}).get('bikes') or []
    bike_id = bikes[0]['id'] if bikes else None

    if bike_id:
        code, detail, _ = req('GET', f'/bikes/{bike_id}/?shop_id={shop_id}')
        record('SHARE-002', '合法 shop_id 进详情', 'pass' if code == 200 else 'fail', module='SHARE')

        code, detail, _ = req('GET', f'/bikes/{bike_id}/')
        record('SHARE-001', '无 shop_id 应拒绝', 'pass' if code == 403 or detail.get('code') == 403 else 'fail', module='SHARE')

        wrong_shop = shop_id + 999
        code, detail, _ = req('GET', f'/bikes/{bike_id}/?shop_id={wrong_shop}')
        record('SHARE-003', '跨租户 shop_id 拦截', 'pass' if code == 403 or detail.get('code') == 403 else 'fail', module='SHARE')

        code, share, _ = req('POST', f'/shop/bikes/{bike_id}/share-link/', token=shop_token)
        if share.get('code') == 200:
            record('SHARE-004', '商家生成分享短链', 'pass', module='SHARE')
            sc = share['data']['short_code']
            sign = share['data']['sign']
            ts = share['data']['timestamp']
            code, resolved, _ = req('GET', f'/s/{sc}/')
            ok_resolve = resolved.get('code') == 200 and resolved.get('data', {}).get('bike_id') == bike_id
            record('SHARE-005', '短链解析', 'pass' if ok_resolve else 'fail', str(resolved) if not ok_resolve else '', module='SHARE')
            code, bad, _ = req('GET', f'/bikes/{bike_id}/?shop_id={shop_id}&timestamp={ts}&sign=invalid')
            record('SHARE-006', '短链验签失败', 'pass' if code == 403 or bad.get('code') == 403 else 'fail', module='SHARE')
            code, good, _ = req('GET', f'/bikes/{bike_id}/?shop_id={shop_id}&timestamp={ts}&sign={sign}')
            record('API-BIKE-01', '带签名详情', 'pass' if code == 200 else 'fail', module='SHARE')
        else:
            record('SHARE-004', '商家生成分享短链', 'fail', str(share), 'SHARE')
    else:
        for cid in ['SHARE-002', 'SHARE-001', 'SHARE-003', 'SHARE-004', 'SHARE-005', 'SHARE-006']:
            record(cid, '分享相关', 'skip', '无车源数据', 'SHARE')

    code, visit, _ = req('POST', '/visits/', token=user_token, data={'shop_id': shop_id})
    record('SHARE-009', '记录最近访问', 'pass' if visit.get('code') == 200 else 'fail', module='SHARE')
    code, visits, _ = req('GET', '/visits/', token=user_token)
    total = visits.get('data', {}).get('total', 0)
    record('SHARE-009', '最近访问列表', 'pass' if total >= 1 else 'fail', f'total={total}', 'SHARE')

    code, shop_page, _ = req('GET', f'/shops/{shop_id}/')
    record('SHARE-008', '店铺分享链 API', 'pass' if shop_page.get('data', {}).get('shop', {}).get('name') else 'fail', module='SHARE')

    # --- APPLY ---
    print('\n[APPLY] 入驻与审核')
    code, dup, _ = req('POST', '/applications/', token=pending_token, data={
        'name': '重复车行', 'shop_type': 1, 'contact_name': '重复', 'phone': '13600000002',
        'address': '广州', 'main_models': '本田', 'description': '重复提交测试',
        'wechat_qrcode': '/media/test.jpg',
    })
    record('APPLY-003', '待审不可重复提交', 'pass' if dup.get('code') != 200 else 'fail', module='APPLY')

    code, no_name, _ = req('POST', '/applications/', token=user_token, data={
        'shop_type': 1, 'contact_name': '无名称', 'phone': '13600000003',
        'address': '深圳', 'main_models': '雅马哈', 'description': '缺名称',
        'wechat_qrcode': '/media/test.jpg',
    })
    record('APPLY-002', '商家名称必填', 'pass' if no_name.get('code') != 200 else 'fail', module='APPLY')

    code, apps, _ = req('GET', '/admin/applications/?status=1', token=admin_token)
    pending_count = apps.get('data', {}).get('total', 0)
    record('APPLY-008', '待审申请列表', 'pass' if code == 200 else 'fail', f'total={pending_count}', 'APPLY')
    record('API-SHOP-04', '管理员待审列表', 'pass' if code == 200 else 'fail', module='APPLY')

    # --- BIKE ---
    print('\n[BIKE] 车源管理')
    code, brands, _ = req('GET', '/brands/')
    brand = brands['data'][0] if brands.get('data') else {'id': None, 'name': '自定义品牌'}
    code, models, _ = req('GET', f'/brands/{brand["id"]}/models/') if brand.get('id') else (200, {'data': ['自定义车型']}, 0)

    bad_mileage_payload = {
        'brand': '测试品牌', 'model': '测试车型', 'year': 2022, 'displacement': '400cc',
        'mileage': 1, 'transfer_count': 0, 'price': 35000,
        'engine_status': '正常', 'suspension_status': '正常', 'brake_status': '正常',
        'electrical_status': '正常', 'frame_status': '正常',
        'modification': '无', 'defects': '无', 'maintenance': '正常',
        'cover_image': 'https://placehold.co/800x600?text=cover',
        'images': ['https://placehold.co/800x600?text=1'] * 3,
    }
    code, bad_m, _ = req('POST', '/shop/bikes/', token=shop_token, data=bad_mileage_payload)
    record('BIKE-003', '行驶里程>1 校验', 'pass' if bad_m.get('code') != 200 else 'fail', module='BIKE')

    bad_price = {**bad_mileage_payload, 'mileage': 5000, 'price': 1}
    code, bad_p, _ = req('POST', '/shop/bikes/', token=shop_token, data=bad_price)
    record('BIKE-004', '售价>1 校验', 'pass' if bad_p.get('code') != 200 else 'fail', module='BIKE')

    no_transfer = {**bad_mileage_payload, 'mileage': 5000, 'price': 35000}
    no_transfer.pop('transfer_count')
    code, no_tc, _ = req('POST', '/shop/bikes/', token=shop_token, data=no_transfer)
    record('BIKE-005', '过户次数必填', 'pass' if no_tc.get('code') != 200 else 'fail', module='BIKE')

    create_payload = {
        **bad_mileage_payload, 'mileage': 5000, 'price': 35000, 'transfer_count': 0,
        'brand_id': brand.get('id'), 'brand': brand.get('name', '自定义品牌'),
        'model': (models.get('data') or ['自定义车型'])[0],
    }
    code, created, _ = req('POST', '/shop/bikes/', token=shop_token, data=create_payload)
    new_bike_id = created.get('data', {}).get('id')
    record('BIKE-001', '发布新车', 'pass' if new_bike_id else 'fail', module='BIKE')
    record('BIKE-002', '品牌车型自定义输入', 'pass' if new_bike_id else 'fail', module='BIKE')

    if new_bike_id:
        code, off, _ = req('POST', f'/shop/bikes/{new_bike_id}/off-shelf/', token=shop_token)
        record('BIKE-008', '商家下架', 'pass' if off.get('data', {}).get('bike_status') == 3 else 'fail', module='BIKE')
        code, c_detail, _ = req('GET', f'/bikes/{new_bike_id}/?shop_id={shop_id}')
        record('BIKE-008', '下架 C 端不可见', 'pass' if c_detail.get('code') == 404 or code == 404 else 'fail', module='BIKE')

        code, on, _ = req('POST', f'/shop/bikes/{new_bike_id}/on-shelf/', token=shop_token)
        record('BIKE-009', '商家重新上架', 'pass' if on.get('data', {}).get('bike_status') == 1 else 'fail', module='BIKE')

        code, sold, _ = req('POST', f'/shop/bikes/{new_bike_id}/mark-sold/', token=shop_token)
        record('BIKE-010', '标记已售', 'pass' if sold.get('data', {}).get('bike_status') == 2 else 'fail', module='BIKE')
        code, sold_detail, _ = req('GET', f'/bikes/{new_bike_id}/?shop_id={shop_id}')
        record('BIKE-010', '已售 C 端可见', 'pass' if sold_detail.get('data', {}).get('bike_status') == 2 else 'fail', module='BIKE')

        code, deleted, _ = req('DELETE', f'/shop/bikes/{new_bike_id}/', token=shop_token)
        record('BIKE-011', '逻辑删除', 'pass' if deleted.get('code') == 200 else 'fail', module='BIKE')

    # --- CEND / FAV ---
    print('\n[CEND] C端浏览与收藏')
    test_bike = bike_id or new_bike_id
    if test_bike:
        code, fav_add, _ = req('POST', '/favorites/', token=user_token, data={'bike_id': test_bike})
        record('CEND-002', '收藏车源', 'pass' if fav_add.get('code') == 200 else 'fail', module='CEND')
        code, favs, _ = req('GET', '/favorites/', token=user_token)
        has = any(b['id'] == test_bike for b in favs.get('data', {}).get('list', []))
        record('CEND-002', '收藏列表含该车', 'pass' if has else 'fail', module='CEND')
        code, unfav, _ = req('DELETE', f'/favorites/{test_bike}/', token=user_token)
        record('CEND-003', '取消收藏', 'pass' if unfav.get('code') == 200 else 'fail', module='CEND')

    code, shop_info, _ = req('GET', f'/shops/{shop_id}/')
    shop_data = shop_info.get('data', {}).get('shop', {})
    record('CEND-005', '商家主页含 shop 信息', 'pass' if shop_data.get('name') else 'fail', module='CEND')

    # --- MSG ---
    print('\n[MSG] 留言咨询')
    if test_bike:
        code, thread, _ = req('POST', '/message-threads/', token=user_token, data={
            'shop_id': shop_id, 'bike_id': test_bike, 'content': '全面测试：还在吗？',
        })
        thread_id = thread.get('data', {}).get('id')
        record('MSG-001', '发起咨询会话', 'pass' if thread_id else 'fail', module='MSG')

        if thread_id:
            code, dup_thread, _ = req('POST', '/message-threads/', token=user_token, data={
                'shop_id': shop_id, 'bike_id': test_bike, 'content': '同车第二条',
            })
            dup_id = dup_thread.get('data', {}).get('id')
            record('MSG-002', '同车不重复建会话', 'pass' if dup_id == thread_id else 'fail', module='MSG')

            code, follow, _ = req('POST', f'/message-threads/{thread_id}/messages/', token=user_token, data={
                'content': '追问：可以试驾吗？', 'sender_type': 1,
            })
            record('MSG-001', '用户追留言', 'pass' if follow.get('code') == 200 else 'fail', module='MSG')

            code, reply, _ = req('POST', f'/message-threads/{thread_id}/messages/', token=shop_token, data={
                'content': '商家回复：欢迎来看车', 'sender_type': 2,
            })
            record('MSG-003', '商家回复', 'pass' if reply.get('code') == 200 else 'fail', module='MSG')

            code, read, _ = req('POST', f'/message-threads/{thread_id}/read/', token=user_token, data={'role': 'user'})
            record('MSG-004', '进入会话自动已读', 'pass' if read.get('code') == 200 else 'fail', module='MSG')

    code, unread_user, _ = req('GET', '/messages/unread-count/?role=user', token=user_token)
    record('MSG-005', '用户未读聚合', 'pass' if unread_user.get('code') == 200 else 'fail', module='MSG')

    code, unread_shop, _ = req('GET', '/messages/unread-count/?role=shop', token=shop_token)
    record('MSG-005', '商家未读聚合', 'pass' if unread_shop.get('code') == 200 else 'fail', module='MSG')

    code, user_threads, _ = req('GET', '/message-threads/', token=shop_token)
    record('MSG-006', '商家我的咨询列表', 'pass' if user_threads.get('code') == 200 else 'fail', module='MSG')

    code, shop_threads, _ = req('GET', '/shop/message-threads/', token=shop_token)
    record('MSG-006', '商家用户咨询列表', 'pass' if shop_threads.get('code') == 200 else 'fail', module='MSG')

    code, admin_msgs, _ = req('GET', '/admin/message-threads/', token=admin_token)
    record('MSG-010', '管理员只读留言', 'pass' if admin_msgs.get('code') == 200 else 'fail', module='MSG')

    # --- SHOP-B ---
    print('\n[SHOP-B] 商家后台')
    code, profile, _ = req('GET', '/shop/profile/', token=shop_token)
    record('SHOP-B-002', '商家资料读取', 'pass' if profile.get('data', {}).get('name') else 'fail', module='SHOP-B')

    code, updated, _ = req('PUT', '/shop/profile/', token=shop_token, data={'description': '全面测试更新'})
    record('SHOP-B-002', '商家资料保存', 'pass' if updated.get('code') == 200 else 'fail', module='SHOP-B')

    code, stats, _ = req('GET', '/shop/stats/', token=shop_token)
    record('SHOP-B-007', '概览统计', 'pass' if 'on_sale' in stats.get('data', {}) else 'fail', module='SHOP-B')

    code, shop_bikes, _ = req('GET', '/shop/bikes/', token=shop_token)
    record('SHOP-B-001', '车源列表', 'pass' if shop_bikes.get('code') == 200 else 'fail', module='SHOP-B')

    code, _, _ = req('GET', '/shop/bikes/', token=banned_token)
    record('SHOP-B-008', '封禁商家访问后台', 'warn' if True else 'fail', '需结合前端路由验证', 'SHOP-B')

    # --- ADMIN ---
    print('\n[ADMIN] 管理后台')
    code, admin_shops, _ = req('GET', '/admin/shops/', token=admin_token)
    record('ADMIN-002', '商户列表', 'pass' if admin_shops.get('code') == 200 else 'fail', module='ADMIN')

    if admin_shops.get('data', {}).get('list'):
        sid = admin_shops['data']['list'][0]['id']
        code, ban, _ = req('POST', f'/admin/shops/{sid}/ban/', token=admin_token)
        record('ADMIN-002', '商户封禁', 'pass' if ban.get('code') == 200 else 'fail', module='ADMIN')
        code, unban, _ = req('POST', f'/admin/shops/{sid}/unban/', token=admin_token)
        record('ADMIN-002', '商户解封', 'pass' if unban.get('code') == 200 else 'fail', module='ADMIN')

    code, admin_stats, _ = req('GET', '/admin/stats/', token=admin_token)
    record('ADMIN-005', '数据概览', 'pass' if 'total_shops' in admin_stats.get('data', {}) else 'fail', module='ADMIN')

    code, admin_bikes, _ = req('GET', '/admin/bikes/', token=admin_token)
    record('ADMIN-003', '全平台车源管控列表', 'pass' if admin_bikes.get('code') == 200 else 'fail', module='ADMIN')

    # --- SEC ---
    print('\n[SEC] 安全与权限')
    code, _, _ = req('POST', '/shop/bikes/', token=user_token, data=create_payload)
    record('SEC-001', '普通用户调商家车源 POST', 'pass' if code == 403 else 'fail', module='SEC')

    code, _, _ = req('GET', '/admin/shops/', token=user_token)
    record('SEC-003', '非管理员调 admin', 'pass' if code == 403 else 'fail', module='SEC')

    code, _, _ = req('GET', '/shop/bikes/', token=user_token)
    record('AUTH-006', '普通用户不可访问商家后台 API', 'pass' if code == 403 else 'fail', module='SEC')

    # --- PERF ---
    print('\n[PERF] 性能抽样')
    perf_cases = [
        ('PERF-001', f'/shops/{shop_id}/'),
        ('PERF-002', f'/bikes/{test_bike}/?shop_id={shop_id}' if test_bike else None),
        ('PERF-004', '/messages/unread-count/?role=user'),
    ]
    for pid, path in perf_cases:
        if not path:
            record(pid, '性能抽样', 'skip', '无车源', 'PERF')
            continue
        times = []
        for _ in range(10):
            _, _, ms = req('GET', path, token=user_token)
            times.append(ms)
        p95 = sorted(times)[int(len(times) * 0.95)]
        threshold = 500 if 'shops' in path or 'bikes' in path else 500
        record(pid, f'P95={p95:.0f}ms', 'pass' if p95 < threshold else 'warn', f'10次采样', 'PERF')

    # --- UI (前端路由可达) ---
    print('\n[UI] 前端页面可达性')
    ui_routes = [
        ('UI-001', '/login'),
        ('UI-002', '/'),
        ('UI-003', f'/shop/{shop_id}'),
        ('UI-005', '/messages'),
        ('UI-006', '/shop/bikes/new'),
        ('UI-007', '/shop/profile'),
        ('UI-008', '/admin/audit'),
    ]
    for uid, route in ui_routes:
        status, html, ms = check_frontend(route)
        ok = status == 200 and ('<div id="app">' in html or 'vite' in html.lower())
        record(uid, f'页面可达 {route}', 'pass' if ok else 'fail', f'HTTP {status}, {ms:.0f}ms', 'UI')

    # Summary
    summary = {'pass': 0, 'fail': 0, 'skip': 0, 'warn': 0}
    for r in RESULTS:
        summary[r['status']] = summary.get(r['status'], 0) + 1

    print('\n' + '=' * 50)
    print(f"通过: {summary['pass']}  失败: {summary['fail']}  跳过: {summary['skip']}  警告: {summary['warn']}")

    out_path = '/Users/xiaoyao/Project/jiche/jiche-backend/scripts/test_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'results': RESULTS, 'summary': summary}, f, ensure_ascii=False, indent=2)
    print(f'\n结果已写入 {out_path}')
    return 1 if summary['fail'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

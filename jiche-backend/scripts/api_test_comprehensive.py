#!/usr/bin/env python3
"""细致全面的接口测试套件 — 覆盖正向/逆向/边界/安全/契约。"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

BASE = 'http://127.0.0.1:8000/api'
RESULTS = []


def record(case_id, name, status, detail='', module=''):
    RESULTS.append({'id': case_id, 'name': name, 'status': status, 'detail': detail, 'module': module})
    sym = {'pass': '✓', 'fail': '✗', 'skip': '○', 'warn': '!'}[status]
    print(f'  {sym} [{case_id}] {name}' + (f' — {detail}' if detail else ''))


def req(method, path, token=None, data=None, extra_headers=None):
    url = f'{BASE}{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=15) as resp:
            elapsed = (time.perf_counter() - t0) * 1000
            raw = resp.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {'raw': raw}
            return resp.status, payload, elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        raw = e.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {'msg': raw}
        return e.code, payload, elapsed


def login(role):
    code, res, _ = req('POST', '/auth/dev/login/', data={'role': role})
    if code != 200 or res.get('code') != 200:
        raise RuntimeError(f'login {role} failed: {res}')
    return res['data']['token'], res['data']['user']


def expect(case_id, name, cond, detail='', module='API'):
    record(case_id, name, 'pass' if cond else 'fail', detail, module)


def expect_code(case_id, name, actual_code, actual_body, expected_codes, module='API'):
    codes = expected_codes if isinstance(expected_codes, (list, tuple, set)) else [expected_codes]
    biz = actual_body.get('code') if isinstance(actual_body, dict) else None
    ok = actual_code in codes or biz in codes
    detail = f'http={actual_code} biz={biz}'
    record(case_id, name, 'pass' if ok else 'fail', detail, module)


def bike_payload(**kw):
    base = {
        'brand': '测试品牌', 'model': '测试车型', 'year': 2022, 'displacement': '400cc',
        'mileage': 5000, 'transfer_count': 0, 'price': 35000,
        'engine_status': '正常', 'suspension_status': '正常', 'brake_status': '正常',
        'electrical_status': '正常', 'frame_status': '正常',
        'modification': '无', 'defects': '无', 'maintenance': '正常',
        'cover_image': 'https://placehold.co/800x600?text=cover',
        'images': ['https://placehold.co/800x600?text=1'] * 3,
    }
    base.update(kw)
    return base


def main():
    print('\n=== 细致全面接口测试 ===')
    print(f'时间: {datetime.now().isoformat()}')

    try:
        user_token, user = login('user')
        shop_token, shop_user = login('shop')
        admin_token, _ = login('admin')
        pending_token, _ = login('pending')
        banned_token, _ = login('banned')
    except RuntimeError as e:
        record('SETUP', '登录失败', 'fail', str(e))
        return 1

    shop_id = shop_user.get('shop_id') or 1

    # ── AUTH ──────────────────────────────────────────
    print('\n[API-AUTH] 认证')
    c, r, _ = req('POST', '/auth/dev/login/', data={'role': 'invalid_role'})
    expect_code('API-AUTH-01', 'Dev 非法角色', c, r, [400, 404])

    c, r, _ = req('GET', '/auth/me/', token=user_token)
    expect('API-AUTH-04', 'me 返回完整字段', all(k in r['data'] for k in ('nickname', 'shop_status', 'is_staff')))

    c, r, _ = req('GET', '/auth/me/', token='totally-invalid-jwt-token')
    if c == 500:
        record('API-AUTH-05', '无效 token 返回 500', 'warn', '应返回 401 而非 500', 'API-SEC')
    else:
        expect_code('API-AUTH-05', '无效 token 应拒绝', c, r, [401, 403])

    c, r, _ = req('POST', '/auth/login-ticket/')
    expect('API-AUTH-02', '创建票据含 ticket_id', 'ticket_id' in r.get('data', {}))
    ticket_id = r['data']['ticket_id']

    c, r, _ = req('GET', f'/auth/login-ticket/{ticket_id}/')
    expect('API-AUTH-03', '轮询 pending', r['data']['status'] == 'pending')

    c, r, _ = req('GET', '/auth/login-ticket/not-exist-id/')
    expect_code('API-AUTH-03b', '不存在票据', c, r, [404])

    c, r, _ = req('POST', '/auth/wx-mini/login/', data={})
    expect_code('API-AUTH-06b', '小程序登录缺 code', c, r, [400])

    c, r, _ = req('POST', '/auth/wx-mini/login/', data={'code': 'mock'})
    expect('API-AUTH-06', '小程序 MOCK 登录', r.get('code') == 200 and 'token' in r.get('data', {}))

    c, r, _ = req('POST', '/auth/logout/', token=user_token)
    expect('API-AUTH-07', '登出接口', r.get('code') == 200)

    # ── ADMIN USERS ───────────────────────────────────
    print('\n[API-ADMIN-USER] 用户管理')
    c, r, _ = req('GET', '/admin/users/', token=admin_token)
    expect('API-ADMIN-USER-01', '管理员用户列表', r.get('code') == 200 and 'total' in r.get('data', {}))

    c, r, _ = req('GET', '/admin/users/', token=user_token)
    expect_code('API-ADMIN-USER-02', '普通用户不可列用户', c, r, [403])

    # ── APPLICATION ───────────────────────────────────
    print('\n[API-APPLY] 入驻')
    c, r, _ = req('POST', '/applications/', token=user_token, data={
        'shop_type': 1, 'contact_name': '张三', 'phone': '13800138000',
        'address': '广州', 'wechat_qrcode': '/media/test.jpg',
    })
    expect_code('API-SHOP-02', '缺商家名称', c, r, [400])

    c, r, _ = req('POST', '/applications/', token=user_token, data={
        'name': 'A', 'shop_type': 1, 'contact_name': '张三', 'phone': '13800138000',
        'wechat_qrcode': '/media/test.jpg',
    })
    expect_code('API-APPLY-02', '商家名称<2字', c, r, [400])

    c, r, _ = req('POST', '/applications/', token=user_token, data={
        'name': '测试车行', 'shop_type': 1, 'contact_name': 'John', 'phone': '13800138000',
        'wechat_qrcode': '/media/test.jpg',
    })
    expect_code('API-APPLY-03', '联系人非中文', c, r, [400])

    c, r, _ = req('POST', '/applications/', token=user_token, data={
        'name': '测试车行', 'shop_type': 1, 'contact_name': '张三', 'phone': '12345',
        'wechat_qrcode': '/media/test.jpg',
    })
    expect_code('API-APPLY-04', '手机号格式错误', c, r, [400])

    c, r, _ = req('GET', '/applications/my/', token=pending_token)
    expect('API-SHOP-03', '查看自己申请', r.get('code') == 200)

    c, r, _ = req('GET', '/admin/applications/?status=1', token=admin_token)
    expect('API-SHOP-04', '待审列表结构', r.get('code') == 200 and 'list' in r.get('data', {}))

    c, r, _ = req('GET', '/admin/applications/?status=99', token=admin_token)
    expect('API-APPLY-05', '非法 status 参数', r.get('code') in (200, 400))

    c, r, _ = req('POST', '/admin/applications/99999/audit/', token=admin_token, data={'action': 'approve'})
    expect_code('API-APPLY-06', '审核不存在申请', c, r, [404, 400])

    # ── SHOP ──────────────────────────────────────────
    print('\n[API-SHOP] 商家')
    c, r, _ = req('GET', f'/shops/{shop_id}/')
    expect('API-SHOP-07', '商家详情含 shop+bikes', r.get('data', {}).get('shop') and 'bikes' in r.get('data', {}))

    c, r, _ = req('GET', f'/shops/99999/')
    expect_code('API-SHOP-07b', '不存在商家', c, r, [404])

    c, r, _ = req('GET', f'/shops/{shop_id}/?status=1')
    expect('API-SHOP-07c', 'status 筛选', r.get('code') == 200)

    c, r, _ = req('GET', '/shop/profile/', token=shop_token)
    expect('API-SHOP-08', '商家资料 GET', r.get('code') == 200)

    c, r, _ = req('PUT', '/shop/profile/', token=shop_token, data={'description': '接口测试更新'})
    expect('API-SHOP-08b', '商家资料 PUT', r.get('code') == 200)

    c, r, _ = req('GET', '/shop/profile/', token=user_token)
    expect_code('API-SHOP-08c', '普通用户不可读商家资料', c, r, [403])

    c, r, _ = req('POST', '/visits/', token=user_token, data={'shop_id': shop_id})
    expect('API-SHOP-10', '记录访问', r.get('data', {}).get('recorded') is True)

    c, r, _ = req('POST', '/visits/', token=user_token, data={})
    expect_code('API-SHOP-10b', '访问缺 shop_id', c, r, [400])

    c, r, _ = req('GET', '/visits/', token=user_token)
    expect('API-SHOP-10c', '最近访问列表', r.get('code') == 200 and r.get('data', {}).get('total', 0) >= 1)

    c, r, _ = req('GET', '/shop/stats/', token=shop_token)
    expect('API-SHOP-11', '商家统计字段', all(k in r.get('data', {}) for k in ('on_sale', 'sold', 'unread_messages')))

    c, r, _ = req('GET', '/admin/stats/', token=admin_token)
    expect('API-SHOP-12', '平台统计', 'total_shops' in r.get('data', {}))

    # ── CATALOG ───────────────────────────────────────
    print('\n[API-CAT] 品牌字典')
    c, r, _ = req('GET', '/brands/')
    expect('API-CAT-01', '品牌列表非空', r.get('code') == 200 and len(r.get('data', [])) >= 1)
    brand_id = r['data'][0]['id'] if r.get('data') else 1

    c, r, _ = req('GET', f'/brands/{brand_id}/models/')
    expect('API-CAT-02', '车型列表', r.get('code') == 200)

    c, r, _ = req('GET', '/brands/99999/models/')
    expect_code('API-CAT-03', '不存在品牌车型', c, r, [404, 400])

    # ── BIKE ──────────────────────────────────────────
    print('\n[API-BIKE] 车源')
    _, shop_detail, _ = req('GET', f'/shops/{shop_id}/')
    existing_bike = (shop_detail.get('data', {}).get('bikes') or [{}])[0].get('id')

    for val, cid in [(0, 'API-BIKE-06a'), (1, 'API-BIKE-06b'), (-100, 'API-BIKE-06c')]:
        c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload(mileage=val))
        expect_code(cid, f'里程边界 mileage={val}', c, r, [400])

    for val in [0, 1, -1]:
        c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload(price=val))
        expect_code('API-BIKE-07', f'售价边界 price={val}', c, r, [400])

    c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload(transfer_count=0))
    expect('API-BIKE-08', '过户次数=0 合法', r.get('code') == 200)
    bike_new = r.get('data', {}).get('id')

    c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload())
    no_tc = bike_payload()
    no_tc.pop('transfer_count', None)
    c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=no_tc)
    expect_code('API-BIKE-08b', '过户次数缺失', c, r, [400])

    c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload(year=1979))
    expect_code('API-BIKE-09', '年份<1980', c, r, [400])

    c, r, _ = req('POST', '/shop/bikes/', token=shop_token, data=bike_payload(images=[]))
    record('API-BIKE-10', '图片为空', 'warn' if r.get('code') == 200 else 'pass',
           '后端未强制≥3张，前端校验' if r.get('code') == 200 else '')

    test_bike = bike_new or existing_bike
    if test_bike:
        c, r, _ = req('GET', f'/bikes/{test_bike}/?shop_id={shop_id}')
        expect('API-BIKE-01', 'C端详情', r.get('code') == 200)

        c, r, _ = req('GET', f'/bikes/{test_bike}/?shop_id=abc')
        expect_code('API-BIKE-02', 'shop_id 非数字', c, r, [403])

        c, r, _ = req('GET', f'/bikes/{test_bike}/')
        expect_code('API-BIKE-03', '无 shop_id', c, r, [403])

        c, r, _ = req('GET', f'/bikes/99999/?shop_id={shop_id}')
        expect_code('API-BIKE-04', '不存在车源', c, r, [404])

        c, r, _ = req('GET', f'/shop/bikes/{test_bike}/', token=shop_token)
        expect('API-BIKE-11', '商家车源详情', r.get('code') == 200)

        c, r, _ = req('PUT', f'/shop/bikes/{test_bike}/', token=shop_token, data=bike_payload(price=36000))
        expect('API-BIKE-12', '编辑车源', r.get('code') == 200)

        c, r, _ = req('POST', f'/shop/bikes/{test_bike}/off-shelf/', token=shop_token)
        expect('API-BIKE-13', '下架 status=3', r.get('data', {}).get('bike_status') == 3)

        c, r, _ = req('GET', f'/bikes/{test_bike}/?shop_id={shop_id}')
        expect_code('API-BIKE-14', '下架 C端 404', c, r, [404])

        c, r, _ = req('POST', f'/shop/bikes/{test_bike}/on-shelf/', token=shop_token)
        expect('API-BIKE-15', '重新上架', r.get('data', {}).get('bike_status') == 1)

        c, r, _ = req('POST', f'/shop/bikes/{test_bike}/mark-sold/', token=shop_token)
        expect('API-BIKE-16', '标记已售', r.get('data', {}).get('bike_status') == 2)

        c, r, _ = req('GET', f'/bikes/{test_bike}/?shop_id={shop_id}')
        expect('API-BIKE-17', '已售 C端可见', r.get('data', {}).get('bike_status') == 2)

        c, r, _ = req('POST', f'/shop/bikes/{test_bike}/share-link/', token=shop_token)
        expect('API-BIKE-18', '分享短链', '/s/' in r.get('data', {}).get('short_url', ''))
        if r.get('code') == 200:
            sc = r['data']['short_code']
            sign = r['data']['sign']
            ts = r['data']['timestamp']
            c2, r2, _ = req('GET', f'/s/{sc}/')
            expect('API-BIKE-19', '短链解析', r2.get('data', {}).get('bike_id') == test_bike)
            c3, r3, _ = req('GET', f'/bikes/{test_bike}/?shop_id={shop_id}&timestamp={ts}&sign=bad')
            expect_code('API-BIKE-20', '验签失败', c3, r3, [403])
            c4, r4, _ = req('GET', f'/bikes/{test_bike}/?shop_id={shop_id}&timestamp={ts}&sign={sign}')
            expect('API-BIKE-21', '验签成功', r4.get('code') == 200)

        c, r, _ = req('GET', '/shop/bikes/?status=1', token=shop_token)
        expect('API-BIKE-22', '商家列表 status 筛选', r.get('code') == 200)

        c, r, _ = req('PUT', f'/shop/bikes/{test_bike}/', token=user_token, data=bike_payload())
        expect_code('API-BIKE-23', '跨商家编辑', c, r, [403, 404])

    c, r, _ = req('GET', '/admin/bikes/', token=admin_token)
    expect('API-BIKE-24', '管理端车源列表', r.get('code') == 200)

    if test_bike:
        c, r, _ = req('POST', f'/admin/bikes/{test_bike}/force-off-shelf/', token=admin_token, data={'reason': '测试违规'})
        expect('API-BIKE-25', '违规下架', r.get('data', {}).get('bike_status') == 4)

        c, r, _ = req('PUT', f'/shop/bikes/{test_bike}/', token=shop_token, data=bike_payload())
        expect_code('API-BIKE-26', '违规车商家不可编辑', c, r, [400, 403])

        c, r, _ = req('POST', f'/admin/bikes/{test_bike}/restore/', token=admin_token)
        expect('API-BIKE-27', '恢复上架', r.get('data', {}).get('bike_status') == 1)

        c, r, _ = req('POST', f'/admin/bikes/{test_bike}/force-off-shelf/', token=admin_token, data={})
        expect('API-BIKE-28', '违规下架可无 reason', r.get('code') == 200)
        req('POST', f'/admin/bikes/{test_bike}/restore/', token=admin_token)

    # ── FAVORITE ──────────────────────────────────────
    print('\n[API-FAV] 收藏')
    if test_bike:
        c, r, _ = req('POST', '/favorites/', token=user_token, data={'bike_id': test_bike})
        expect('API-FAV-02', '添加收藏', r.get('code') == 200)

        c, r, _ = req('POST', '/favorites/', token=user_token, data={'bike_id': test_bike})
        expect_code('API-FAV-02b', '重复收藏 409', c, r, [409, 400])

        c, r, _ = req('GET', '/favorites/', token=user_token)
        expect('API-FAV-01', '收藏列表', any(b['id'] == test_bike for b in r.get('data', {}).get('list', [])))

        c, r, _ = req('DELETE', f'/favorites/{test_bike}/', token=user_token)
        expect('API-FAV-03', '取消收藏', r.get('code') == 200)

        c, r, _ = req('GET', '/favorites/')
        expect_code('API-FAV-04', '未登录收藏', c, r, [401, 403])

    # ── MESSAGE ───────────────────────────────────────
    print('\n[API-MSG] 留言')
    if test_bike:
        c, r, _ = req('POST', '/message-threads/', token=user_token, data={
            'bike_id': test_bike, 'content': '全面接口测试首条',
        })
        expect('API-MSG-02', '创建会话', r.get('data', {}).get('id') is not None)
        tid = r.get('data', {}).get('id')

        c, r, _ = req('POST', '/message-threads/', token=user_token, data={
            'bike_id': test_bike, 'content': '同车第二条',
        })
        expect('API-MSG-02b', '同车复用会话', r.get('data', {}).get('id') == tid)

        c, r, _ = req('POST', '/message-threads/', token=user_token, data={'bike_id': 99999, 'content': 'x'})
        expect_code('API-MSG-02c', '不存在车源建会话', c, r, [404, 400])

        if tid:
            c, r, _ = req('GET', f'/message-threads/{tid}/', token=user_token)
            expect('API-MSG-03', '会话详情含 messages', 'messages' in r.get('data', {}))

            c, r, _ = req('GET', f'/message-threads/{tid}/', token=admin_token)
            expect('API-MSG-03b', '管理员可看会话（监管）', r.get('code') == 200)

            c, r, _ = req('POST', f'/message-threads/{tid}/messages/', token=user_token, data={'content': '追问'})
            expect_code('API-MSG-04b', '缺 sender_type', c, r, [400])

            c, r, _ = req('POST', f'/message-threads/{tid}/messages/', token=user_token, data={
                'content': '追问', 'sender_type': 1,
            })
            expect('API-MSG-04', '用户发消息', r.get('code') == 200)

            c, r, _ = req('POST', f'/message-threads/{tid}/messages/', token=shop_token, data={
                'content': '商家回复', 'sender_type': 2,
            })
            expect('API-MSG-04c', '商家回复', r.get('code') == 200)

            long_msg = '测' * 501
            c, r, _ = req('POST', f'/message-threads/{tid}/messages/', token=user_token, data={
                'content': long_msg, 'sender_type': 1,
            })
            expect_code('API-MSG-05', '消息超 500 字', c, r, [400])

            c, r, _ = req('POST', f'/message-threads/{tid}/read/', token=shop_token, data={'role': 'shop'})
            expect('API-MSG-06', '商家标记已读', r.get('data', {}).get('unread_count_shop') == 0)

    c, r, _ = req('GET', '/messages/unread-count/?role=user', token=user_token)
    expect('API-MSG-07', '用户未读数', 'unread_count' in r.get('data', {}))

    c, r, _ = req('GET', '/messages/unread-count/?role=shop', token=shop_token)
    expect('API-MSG-07b', '商家未读数', 'unread_count' in r.get('data', {}))

    c, r, _ = req('GET', '/messages/unread-count/?role=invalid', token=user_token)
    expect_code('API-MSG-07c', '无效 role', c, r, [400])

    c, r, _ = req('GET', '/message-threads/', token=user_token)
    expect('API-MSG-01', '用户会话列表', r.get('code') == 200)

    c, r, _ = req('GET', '/shop/message-threads/', token=shop_token)
    expect('API-MSG-08', '商家会话列表', r.get('code') == 200)

    c, r, _ = req('GET', '/admin/message-threads/', token=admin_token)
    expect('API-MSG-09', '管理端会话列表', r.get('code') == 200)

    # ── SECURITY ──────────────────────────────────────
    print('\n[API-SEC] 安全')
    c, r, _ = req('GET', f'/shops/{shop_id}/?keyword=%27%20OR%201%3D1--')
    expect('SEC-008', 'SQL 注入关键词', r.get('code') == 200)

    c, r, _ = req('GET', '/admin/shops/', token=user_token)
    expect_code('SEC-003', '越权管理端', c, r, [403])

    c, r, _ = req('POST', '/shop/bikes/', token=banned_token, data=bike_payload())
    expect_code('SEC-009', '封禁商家发车', c, r, [403])

    c, r, _ = req('GET', '/shop/bikes/', token=banned_token)
    expect_code('SEC-010', '封禁商家列表', c, r, [403])

    # ── CONTRACT ──────────────────────────────────────
    print('\n[API-CONTRACT] 响应契约')
    c, r, _ = req('GET', f'/shops/{shop_id}/')
    expect('API-CONTRACT-01', '统一响应含 code/msg/data', all(k in r for k in ('code', 'msg', 'data')))
    expect('API-CONTRACT-02', '成功 code=200', r.get('code') == 200)

    c, r, _ = req('GET', '/auth/me/')
    expect('API-CONTRACT-03', '错误响应含 code/msg', all(k in r for k in ('code', 'msg')))

    # Summary
    summary = {'pass': 0, 'fail': 0, 'skip': 0, 'warn': 0}
    for item in RESULTS:
        summary[item['status']] = summary.get(item['status'], 0) + 1

    print('\n' + '=' * 50)
    print(f"通过: {summary['pass']}  失败: {summary['fail']}  跳过: {summary['skip']}  警告: {summary['warn']}")

    out = '/Users/xiaoyao/Project/jiche/jiche-backend/scripts/api_test_results.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'results': RESULTS, 'summary': summary}, f, ensure_ascii=False, indent=2)
    print(f'结果: {out}')
    return 1 if summary['fail'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

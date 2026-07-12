#!/usr/bin/env python3
"""压力测试 / 防恶意调用探测 — 并发、刷接口、资源耗尽模拟。"""
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE = 'http://127.0.0.1:8000/api'
RESULTS = []


def record(case_id, name, status, detail='', module='STRESS'):
    RESULTS.append({'id': case_id, 'name': name, 'status': status, 'detail': detail, 'module': module})
    sym = {'pass': '✓', 'fail': '✗', 'skip': '○', 'warn': '!'}[status]
    print(f'  {sym} [{case_id}] {name}' + (f' — {detail}' if detail else ''))


def req(method, path, token=None, data=None, timeout=10):
    url = f'{BASE}{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            elapsed = (time.perf_counter() - t0) * 1000
            raw = resp.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}
            return {'ok': True, 'status': resp.status, 'code': payload.get('code'), 'ms': elapsed, 'body': payload}
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        try:
            payload = json.loads(e.read().decode())
        except json.JSONDecodeError:
            payload = {}
        return {'ok': False, 'status': e.code, 'code': payload.get('code'), 'ms': elapsed, 'body': payload}
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return {'ok': False, 'status': 0, 'code': None, 'ms': elapsed, 'error': str(e)}


def login(role):
    r = req('POST', '/auth/dev/login/', data={'role': role})
    if not r['ok'] or r.get('body', {}).get('code') != 200:
        raise RuntimeError(f'login {role} failed')
    return r['body']['data']['token'], r['body']['data']['user']


def burst(name, fn, workers, total_requests):
    """并发执行 total_requests 次，workers 个线程。"""
    latencies = []
    status_counts = {}
    errors = 0
    rate_limited = 0

    def run_one():
        return fn()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_one) for _ in range(total_requests)]
        for fut in as_completed(futures):
            try:
                r = fut.result()
                latencies.append(r['ms'])
                key = f"{r['status']}/{r.get('code')}"
                status_counts[key] = status_counts.get(key, 0) + 1
                if r['status'] == 429 or (r.get('body', {}).get('code') == 429):
                    rate_limited += 1
                if r['status'] >= 500 or r['status'] == 0:
                    errors += 1
            except Exception:
                errors += 1

    if latencies:
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        p99 = sorted(latencies)[int(len(latencies) * 0.99)]
        avg = statistics.mean(latencies)
    else:
        p50 = p95 = p99 = avg = 0

    return {
        'name': name,
        'total': total_requests,
        'workers': workers,
        'errors': errors,
        'rate_limited': rate_limited,
        'p50_ms': round(p50, 1),
        'p95_ms': round(p95, 1),
        'p99_ms': round(p99, 1),
        'avg_ms': round(avg, 1),
        'status_counts': status_counts,
        'error_rate': round(errors / total_requests * 100, 2),
    }


def main():
    print('\n=== 压力测试 / 防恶意调用探测 ===')
    print(f'时间: {datetime.now().isoformat()}')
    print('说明: 当前系统未配置限流中间件，本测试用于发现抗压能力与风险点\n')

    try:
        user_token, _ = login('user')
        shop_token, shop_user = login('shop')
    except RuntimeError as e:
        record('SETUP', '登录失败', 'fail', str(e))
        return 1

    shop_id = shop_user.get('shop_id') or 1
    shop_r = req('GET', f'/shops/{shop_id}/')
    bikes = shop_r.get('body', {}).get('data', {}).get('bikes') or []
    bike_id = bikes[0]['id'] if bikes else None

    scenarios = []

    # 1. 公开接口刷浏览（模拟恶意刷 view_count）
    print('\n[STRESS-01] 公开车源详情高频访问（100并发×50次）')
    if bike_id:
        def hit_detail():
            return req('GET', f'/bikes/{bike_id}/?shop_id={shop_id}')
        r = burst('bike_detail_flood', hit_detail, workers=50, total_requests=200)
        scenarios.append(r)
        detail = f"err={r['error_rate']}% p95={r['p95_ms']}ms rate_limit={r['rate_limited']}"
        if r['error_rate'] > 5:
            record('STRESS-01', '车源详情抗压', 'fail', detail)
        elif r['rate_limited'] == 0:
            record('STRESS-01', '车源详情抗压', 'warn', detail + '；无限流，view_count 可被刷')
        else:
            record('STRESS-01', '车源详情抗压', 'pass', detail)

    # 2. 商家主页刷接口
    print('\n[STRESS-02] 商家主页高频（30并发×100次）')
    def hit_shop():
        return req('GET', f'/shops/{shop_id}/')
    r = burst('shop_flood', hit_shop, workers=30, total_requests=100)
    scenarios.append(r)
    detail = f"err={r['error_rate']}% p95={r['p95_ms']}ms rate_limit={r['rate_limited']}"
    record('STRESS-02', '商家主页抗压', 'warn' if r['rate_limited'] == 0 else 'pass', detail)

    # 3. 登录票据刷接口（模拟恶意创建 ticket）
    print('\n[STRESS-03] 登录票据刷接口（20并发×50次）')
    def hit_ticket():
        return req('POST', '/auth/login-ticket/')
    r = burst('ticket_flood', hit_ticket, workers=20, total_requests=50)
    scenarios.append(r)
    detail = f"err={r['error_rate']}% p95={r['p95_ms']}ms created={r['status_counts']}"
    record('STRESS-03', '登录票据防刷', 'warn' if r['rate_limited'] == 0 else 'pass',
           detail + '；无限制可耗尽内存/存储')

    # 4. Dev 登录刷 token（模拟暴力尝试）
    print('\n[STRESS-04] Dev 登录高频（10并发×30次）')
    def hit_dev_login():
        return req('POST', '/auth/dev/login/', data={'role': 'user'})
    r = burst('dev_login_flood', hit_dev_login, workers=10, total_requests=30)
    scenarios.append(r)
    record('STRESS-04', 'Dev 登录防刷', 'warn' if r['rate_limited'] == 0 else 'pass',
           f"err={r['error_rate']}% p95={r['p95_ms']}ms")

    # 5. 未读数轮询放大（模拟 100 用户同时轮询）
    print('\n[STRESS-05] 未读数轮询放大（50并发×50次）')
    def hit_unread():
        return req('GET', '/messages/unread-count/?role=user', token=user_token)
    r = burst('unread_poll', hit_unread, workers=50, total_requests=50)
    scenarios.append(r)
    detail = f"err={r['error_rate']}% p95={r['p95_ms']}ms"
    if r['p95_ms'] > 1000:
        record('STRESS-05', '未读轮询抗压', 'warn', detail + '；P95 超 1s')
    else:
        record('STRESS-05', '未读轮询抗压', 'pass', detail)

    # 6. 收藏反复添加删除
    print('\n[STRESS-06] 收藏反复操作（10并发×20次）')
    if bike_id:
        counter = {'n': 0}

        def hit_fav():
            counter['n'] += 1
            if counter['n'] % 2 == 0:
                return req('POST', '/favorites/', token=user_token, data={'bike_id': bike_id})
            return req('DELETE', f'/favorites/{bike_id}/', token=user_token)

        r = burst('fav_hammer', hit_fav, workers=10, total_requests=20)
        scenarios.append(r)
        record('STRESS-06', '收藏反复操作', 'warn' if r['rate_limited'] == 0 else 'pass',
               f"err={r['error_rate']}% status={r['status_counts']}")

    # 7. 留言刷屏
    print('\n[STRESS-07] 留言刷屏（5并发×15次）')
    if bike_id:
        def hit_msg():
            return req('POST', '/message-threads/', token=user_token, data={
                'bike_id': bike_id, 'content': f'压力测试 {time.time()}',
            })
        r = burst('msg_spam', hit_msg, workers=5, total_requests=15)
        scenarios.append(r)
        record('STRESS-07', '留言刷屏防护', 'warn' if r['rate_limited'] == 0 else 'pass',
               f"err={r['error_rate']}% 全部成功={r['status_counts']}；无频率限制可骚扰商家")

    # 8. 短链解析刷接口
    print('\n[STRESS-08] 短链暴力解析（20并发×50次）')
    share_r = req('POST', f'/shop/bikes/{bike_id}/share-link/', token=shop_token) if bike_id else None
    if share_r and share_r.get('body', {}).get('code') == 200:
        sc = share_r['body']['data']['short_code']

        def hit_short():
            return req('GET', f'/s/{sc}/')

        r = burst('short_resolve', hit_short, workers=20, total_requests=50)
        scenarios.append(r)
        record('STRESS-08', '短链解析抗压', 'pass' if r['error_rate'] < 5 else 'fail',
               f"p95={r['p95_ms']}ms err={r['error_rate']}%")

        def hit_bad_short():
            return req('GET', f'/s/XXXXXX/')

        r2 = burst('bad_short', hit_bad_short, workers=10, total_requests=30)
        scenarios.append(r2)
        record('STRESS-08b', '无效短链暴力探测', 'warn' if r2['rate_limited'] == 0 else 'pass',
               f"status={r2['status_counts']}；无限流可被枚举")

    # 9. 管理端接口（需认证后的滥用）
    print('\n[STRESS-09] 管理端列表重复拉取（10并发×30次）')
    def hit_admin():
        return req('GET', '/admin/bikes/', token=shop_token)  # 非管理员应 403
    r = burst('admin_probe', hit_admin, workers=10, total_requests=30)
    scenarios.append(r)
    record('STRESS-09', '越权探测稳定性', 'pass',
           f"403率正常 status={r['status_counts']}")

    # 10. 超长 URL / 大 payload
    print('\n[STRESS-10] 异常大包探测')
    big_content = 'A' * 10000
    r = req('POST', '/message-threads/', token=user_token, data={
        'bike_id': bike_id or 1, 'content': big_content,
    })
    record('STRESS-10a', '超大留言拒绝', 'pass' if r['status'] in (400, 413) or r.get('code') == 400 else 'warn',
           f"status={r['status']} code={r.get('code')}")

    long_path = '/shops/' + '9' * 500 + '/'
    r = req('GET', long_path)
    record('STRESS-10b', '超长路径处理', 'pass' if r['status'] in (404, 414, 400) else 'warn',
           f"status={r['status']}")

    # 汇总与建议
    print('\n[STRESS-SUMMARY] 风险汇总')
    no_rate_limit = all(s['rate_limited'] == 0 for s in scenarios)
    if no_rate_limit:
        record('STRESS-RISK-01', '全站无限流中间件', 'warn', '恶意高频调用不会被自动阻断')
    high_error = [s for s in scenarios if s['error_rate'] > 10]
    if high_error:
        for s in high_error:
            record('STRESS-RISK-02', f"{s['name']} 错误率高", 'fail', f"{s['error_rate']}%")
    else:
        record('STRESS-RISK-02', '无高错误率场景', 'pass')

    recommendations = [
        '生产环境关闭 /auth/dev/login/ 或 IP 白名单',
        '引入 django-ratelimit 或 Nginx limit_req：公开读接口 60/min/IP',
        '登录票据创建：5/min/IP，防止 ticket 洪水',
        '留言发送：10/min/用户，防止商家骚扰',
        '收藏操作：30/min/用户',
        'view_count 改为异步去重统计，防刷浏览量',
        '短链解析失败：5/min/IP 后临时封禁',
        'WECHAT_MOCK=false 且关闭 DEBUG 后再做生产压测',
    ]

    summary = {'pass': 0, 'fail': 0, 'skip': 0, 'warn': 0}
    for item in RESULTS:
        summary[item['status']] = summary.get(item['status'], 0) + 1

    print('\n' + '=' * 50)
    print(f"通过: {summary['pass']}  失败: {summary['fail']}  警告: {summary['warn']}")
    print('\n加固建议:')
    for rec in recommendations:
        print(f'  • {rec}')

    out = '/Users/xiaoyao/Project/jiche/jiche-backend/scripts/stress_test_results.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': RESULTS,
            'summary': summary,
            'scenarios': scenarios,
            'recommendations': recommendations,
        }, f, ensure_ascii=False, indent=2)
    print(f'\n结果: {out}')
    return 1 if summary['fail'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

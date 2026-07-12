#!/usr/bin/env python3
"""移动端兼容性测试 — viewport、UA、响应式断点、微信浏览器、路由可达。"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

FRONTEND = 'http://127.0.0.1:5173'
FRONTEND_SRC = Path(__file__).resolve().parents[2] / 'jiche-frontend'
RESULTS = []

MOBILE_UAS = {
    'iPhone Safari': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ),
    'Android Chrome': (
        'Mozilla/5.0 (Linux; Android 14; Pixel 8) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ),
    'WeChat iOS': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
        'MicroMessenger/8.0.43(0x18002b2d) NetType/WIFI Language/zh_CN'
    ),
    'WeChat Android': (
        'Mozilla/5.0 (Linux; Android 14; SM-S911B) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
        'Chrome/120.0.6099.210 Mobile Safari/537.36 '
        'MicroMessenger/8.0.43(0x28002b3d) Process/toolsmp NetType/WIFI Language/zh_CN'
    ),
    'iPad Safari': (
        'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ),
}

MOBILE_ROUTES = [
    ('/', '首页'),
    ('/login', '登录'),
    ('/shop/1', '商家主页'),
    ('/bike/1?shop_id=1', '商品详情'),
    ('/favorites', '收藏'),
    ('/messages', '咨询'),
    ('/profile', '我的'),
    ('/apply-shop', '入驻'),
    ('/shop/dashboard', '商家概览'),
    ('/shop/bikes', '商家车源'),
    ('/shop/bikes/new', '发布车源'),
    ('/shop/profile', '商家资料'),
    ('/admin/audit', '商家审核'),
]

REQUIRED_MOBILE_FILES = [
    'src/layouts/UserLayout.vue',
    'src/layouts/ShopLayout.vue',
    'src/layouts/AdminLayout.vue',
    'src/views/user/BikeDetail.vue',
    'src/components/NavBar.vue',
]


def record(case_id, name, status, detail='', module='MOBILE'):
    RESULTS.append({'id': case_id, 'name': name, 'status': status, 'detail': detail, 'module': module})
    sym = {'pass': '✓', 'fail': '✗', 'skip': '○', 'warn': '!'}[status]
    print(f'  {sym} [{case_id}] {name}' + (f' — {detail}' if detail else ''))


def fetch(url, user_agent=None):
    headers = {}
    if user_agent:
        headers['User-Agent'] = user_agent
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), {}
    except Exception as e:
        return 0, str(e), {}


def count_media_queries(directory, breakpoint='768px'):
    pattern = re.compile(r'@media\s*\([^)]*max-width\s*:\s*' + re.escape(breakpoint))
    total = 0
    files_with = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if not fname.endswith(('.vue', '.css')):
                continue
            path = Path(root) / fname
            try:
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            matches = pattern.findall(text)
            if matches:
                total += len(matches)
                rel = path.relative_to(directory)
                files_with.append(str(rel))
    return total, files_with


def main():
    print('\n=== 移动端兼容性测试 ===')
    print(f'时间: {datetime.now().isoformat()}')

    # 1. viewport meta
    print('\n[MOBILE-VIEWPORT]')
    index_path = FRONTEND_SRC / 'index.html'
    if index_path.exists():
        html = index_path.read_text(encoding='utf-8')
        has_viewport = 'viewport' in html and 'width=device-width' in html
        has_fit = 'viewport-fit=cover' in html
        record('MOB-001', 'viewport meta 存在', 'pass' if has_viewport else 'fail')
        record('MOB-002', 'viewport-fit=cover（刘海屏）', 'pass' if has_fit else 'warn', '建议保留')
        record('MOB-003', 'lang=zh-CN', 'pass' if 'lang="zh-CN"' in html else 'warn')
    else:
        record('MOB-001', 'index.html', 'fail', '文件不存在')

    # 2. 响应式 CSS 断点
    print('\n[MOBILE-RESPONSIVE]')
    src_dir = FRONTEND_SRC / 'src'
    mq_count, mq_files = count_media_queries(src_dir)
    record('MOB-010', f'768px 断点 @media 数量', 'pass' if mq_count >= 8 else 'warn', f'共 {mq_count} 处')

    for rel in REQUIRED_MOBILE_FILES:
        full = FRONTEND_SRC / rel
        if full.exists():
            text = full.read_text(encoding='utf-8')
            has_mq = '@media' in text and '768' in text
            record('MOB-011', f'{rel} 含移动端样式', 'pass' if has_mq else 'warn')
        else:
            record('MOB-011', rel, 'fail', '文件缺失')

    # UserLayout 移动端 TabBar
    ul = FRONTEND_SRC / 'src/layouts/UserLayout.vue'
    if ul.exists():
        text = ul.read_text(encoding='utf-8')
        record('MOB-012', 'C端 mobile-tabbar 组件', 'pass' if 'mobile-tabbar' in text else 'fail')
        record('MOB-013', 'isMobile 断点 <=768', 'pass' if '768' in text and 'isMobile' in text else 'fail')

    # BikeDetail 底栏
    bd = FRONTEND_SRC / 'src/views/user/BikeDetail.vue'
    if bd.exists():
        text = bd.read_text(encoding='utf-8')
        record('MOB-014', '详情页移动端底栏', 'pass' if 'bottom-bar' in text or '900px' in text else 'warn')

    # 3. 多 UA 路由可达
    print('\n[MOBILE-UA] 多设备 User-Agent')
    for ua_name, ua in MOBILE_UAS.items():
        status, body, _ = fetch(f'{FRONTEND}/', ua)
        ok = status == 200 and '<div id="app">' in body
        record('MOB-020', f'{ua_name} 访问首页', 'pass' if ok else 'fail', f'HTTP {status}')

    # 4. 关键路由多 UA
    print('\n[MOBILE-ROUTE] 关键路由（微信 iOS UA）')
    wechat_ua = MOBILE_UAS['WeChat iOS']
    for route, label in MOBILE_ROUTES:
        status, body, _ = fetch(f'{FRONTEND}{route}', wechat_ua)
        ok = status == 200 and ('<div id="app">' in body or 'vite' in body.lower())
        record('MOB-021', f'{label} {route}', 'pass' if ok else 'fail', f'HTTP {status}')

    # 5. 触控/移动端 API 检查（源码）
    print('\n[MOBILE-UX] 移动端体验源码检查')
    navbar = FRONTEND_SRC / 'src/components/NavBar.vue'
    if navbar.exists():
        text = navbar.read_text(encoding='utf-8')
        record('MOB-030', 'NavBar 移动端折叠', 'pass' if '768' in text else 'warn')

    shop_audit = FRONTEND_SRC / 'src/views/admin/ShopAudit.vue'
    if shop_audit.exists():
        text = shop_audit.read_text(encoding='utf-8')
        record('MOB-031', '审核页移动卡片布局', 'pass' if 'mobile' in text.lower() or '768' in text else 'warn')

    bike_list = FRONTEND_SRC / 'src/views/shop/BikeList.vue'
    if bike_list.exists():
        text = bike_list.read_text(encoding='utf-8')
        record('MOB-032', '商家车源移动列表', 'pass' if 'mobile' in text.lower() else 'warn')

    # 6. 安全区 / 字体
    style = FRONTEND_SRC / 'src/style.css'
    if style.exists():
        text = style.read_text(encoding='utf-8')
        record('MOB-040', '全局样式存在', 'pass' if len(text) > 100 else 'fail')

    summary = {'pass': 0, 'fail': 0, 'skip': 0, 'warn': 0}
    for item in RESULTS:
        summary[item['status']] = summary.get(item['status'], 0) + 1

    print('\n' + '=' * 50)
    print(f"通过: {summary['pass']}  失败: {summary['fail']}  警告: {summary['warn']}")

    manual = [
        'MOB-M01 iPhone 实机：底部 TabBar 不遮挡内容',
        'MOB-M02 微信内置浏览器：扫码登录页展示正常',
        'MOB-M03 横屏 iPad：管理后台侧栏可用',
        'MOB-M04 商品详情：轮播手势滑动',
        'MOB-M05 软键盘弹出：聊天输入框不被遮挡',
        'MOB-M06 安全区域：iPhone 刘海屏底栏 padding',
    ]
    print('\n需实机人工验证:')
    for m in manual:
        print(f'  - {m}')

    out = '/Users/xiaoyao/Project/jiche/jiche-backend/scripts/mobile_compat_results.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': RESULTS,
            'summary': summary,
            'manual_checklist': manual,
        }, f, ensure_ascii=False, indent=2)
    print(f'结果: {out}')
    return 1 if summary['fail'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

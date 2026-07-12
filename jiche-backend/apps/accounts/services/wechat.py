from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Optional

import requests
from django.conf import settings


@dataclass
class WeChatSession:
    openid: str
    unionid: Optional[str] = None
    session_key: Optional[str] = None


class WeChatServiceError(Exception):
    pass


class WeChatService:
    MINI_LOGIN_URL = 'https://api.weixin.qq.com/sns/jscode2session'

    def code_to_session(self, code: str, *, platform: str = 'mini_program') -> WeChatSession:
        if settings.WECHAT_MOCK:
            return self._mock_session(code, platform=platform)
        if platform == 'mini_program':
            return self._mini_code_to_session(code)
        raise WeChatServiceError('当前仅支持小程序 code2session，Web 扫码请使用开放平台接口')

    def _mock_session(self, code: str, *, platform: str) -> WeChatSession:
        digest = hashlib.sha256(f'{platform}:{code}'.encode()).hexdigest()
        openid_prefix = 'mp' if platform == 'mini_program' else 'web'
        unionid = f'union_{digest[:16]}'
        openid = f'{openid_prefix}_{digest[16:32]}'
        return WeChatSession(openid=openid, unionid=unionid, session_key='mock_session_key')

    def _mini_code_to_session(self, code: str) -> WeChatSession:
        app_id = settings.WECHAT_MINI_APP_ID
        app_secret = settings.WECHAT_MINI_APP_SECRET
        if not app_id or not app_secret:
            raise WeChatServiceError('未配置 WECHAT_MINI_APP_ID / WECHAT_MINI_APP_SECRET')

        response = requests.get(
            self.MINI_LOGIN_URL,
            params={
                'appid': app_id,
                'secret': app_secret,
                'js_code': code,
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )
        payload = response.json()
        if payload.get('errcode'):
            raise WeChatServiceError(payload.get('errmsg') or '微信登录失败')
        return WeChatSession(
            openid=payload['openid'],
            unionid=payload.get('unionid'),
            session_key=payload.get('session_key'),
        )

    def build_qr_placeholder_url(self, ticket_id: str) -> str:
        text = f'微信扫码登录\\n{ticket_id}'
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220">'
            f'<rect fill="#ffffff" width="220" height="220"/>'
            f'<text x="50%" y="45%" font-size="16" text-anchor="middle" fill="#07c160" '
            f'font-family="sans-serif" font-weight="bold">{text}</text>'
            f'</svg>'
        )
        from urllib.parse import quote

        return f'data:image/svg+xml,{quote(svg)}'

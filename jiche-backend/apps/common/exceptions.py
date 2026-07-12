from rest_framework import status
from rest_framework.views import exception_handler

from apps.common.response import error_response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        msg = response.data
        if isinstance(msg, dict):
            if 'detail' in msg:
                detail = msg['detail']
                msg = detail if isinstance(detail, str) else str(detail)
            else:
                msg = '; '.join(
                    f'{key}: {value[0] if isinstance(value, list) else value}'
                    for key, value in msg.items()
                )
        elif isinstance(msg, list):
            msg = msg[0] if msg else '请求失败'
        return error_response(msg=str(msg), code=response.status_code, status=response.status_code)
    return response

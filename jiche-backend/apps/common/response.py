from rest_framework.response import Response


def success_response(data=None, msg='success', code=200, status=200):
    return Response({'code': code, 'msg': msg, 'data': data}, status=status)


def error_response(msg='error', code=400, data=None, status=400):
    return Response({'code': code, 'msg': msg, 'data': data}, status=status)

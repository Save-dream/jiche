from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticatedUser, IsPlatformAdmin, IsShopMerchant
from apps.common.response import error_response, success_response
from apps.messaging.serializers import CreateThreadSerializer, MarkReadSerializer, SendMessageSerializer
from apps.messaging.services.message_service import MessageService, MessageServiceError
from apps.shops.models import Shop


class MessageThreadListCreateView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        data = MessageService().list_user_threads(request.user)
        return success_response(data)

    def post(self, request):
        serializer = CreateThreadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = MessageService()
        try:
            data = service.create_or_append_thread(
                request.user,
                bike_id=serializer.validated_data['bike_id'],
                content=serializer.validated_data['content'],
                contact_phone=serializer.validated_data.get('contact_phone', ''),
            )
        except MessageServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class MessageThreadDetailView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request, thread_id):
        service = MessageService()
        try:
            data = service.get_thread(thread_id, request.user)
        except MessageServiceError as exc:
            code = 403 if '无权' in str(exc) else 404
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class MessageThreadSendView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request, thread_id):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = MessageService()
        try:
            data = service.send_message(
                thread_id,
                request.user,
                content=serializer.validated_data['content'],
                sender_type=serializer.validated_data['sender_type'],
            )
        except MessageServiceError as exc:
            if '无权' in str(exc):
                return error_response(str(exc), code=403, status=403)
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class MessageThreadReadView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request, thread_id):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = MessageService()
        try:
            data = service.mark_read(thread_id, request.user, serializer.validated_data['role'])
        except MessageServiceError as exc:
            code = 403 if '无权' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class ShopMessageThreadListView(APIView):
    permission_classes = [IsShopMerchant]

    def get(self, request):
        shop = Shop.objects.filter(id=request.user.shop_id, is_deleted=False).first()
        if not shop:
            return error_response('商家信息不存在', code=400)
        status_param = request.query_params.get('status')
        status = int(status_param) if status_param else None
        data = MessageService().list_shop_threads(shop.id, status=status)
        return success_response(data)


class AdminMessageThreadListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        data = MessageService().list_admin_threads()
        return success_response(data)


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        role = request.query_params.get('role', 'user')
        if role not in ('user', 'shop'):
            return error_response('无效的角色参数', code=400)
        data = MessageService().unread_count(request.user, role=role)
        return success_response(data)

from typing import Optional

from django.core.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticatedUser, IsPlatformAdmin, IsShopMerchant
from apps.common.response import error_response, success_response
from apps.shops.serializers import (
    BanShopSerializer,
    RecordVisitSerializer,
    ShopApplicationAuditSerializer,
    ShopApplicationSubmitSerializer,
    ShopProfileUpdateSerializer,
)
from apps.shops.services.application_service import ApplicationService, ApplicationServiceError
from apps.shops.services.shop_service import ShopService, ShopServiceError
from apps.shops.utils.upload import save_uploaded_image


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticatedUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return error_response('请上传图片文件', code=400)
        try:
            url = save_uploaded_image(uploaded_file)
        except ValidationError as exc:
            return error_response(str(exc), code=400)
        return success_response({'url': url})


class SubmitApplicationView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        serializer = ShopApplicationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ApplicationService()
        try:
            data = service.submit_application(request.user, serializer.validated_data)
        except ApplicationServiceError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class MyApplicationView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        service = ApplicationService()
        application = service.get_my_application(request.user)
        return success_response(application)


class AdminApplicationListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        status_param = request.query_params.get('status')
        status = int(status_param) if status_param else None
        service = ApplicationService()
        data = service.list_applications(status=status)
        return success_response(data)


class AdminApplicationAuditView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, application_id):
        serializer = ShopApplicationAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ApplicationService()
        try:
            data = service.audit_application(
                application_id=application_id,
                auditor=request.user,
                action=serializer.validated_data['action'],
                reject_reason=serializer.validated_data.get('reject_reason', ''),
            )
        except ApplicationServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code)
        return success_response(data)


class ShopDetailView(APIView):
    def get(self, request, shop_id):
        status_param = request.query_params.get('status')
        status = int(status_param) if status_param else None
        service = ShopService()
        try:
            data = service.get_shop_detail(shop_id, status=status)
        except ShopServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class ShopProfileView(APIView):
    permission_classes = [IsShopMerchant]

    def get(self, request):
        service = ShopService()
        try:
            data = service.get_merchant_profile(request.user)
        except ShopServiceError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)

    def put(self, request):
        serializer = ShopProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ShopService()
        try:
            data = service.update_merchant_profile(request.user, serializer.validated_data)
        except ShopServiceError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class AdminShopListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        data = ShopService().list_admin_shops()
        return success_response(data)


class AdminShopBanView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, shop_id):
        serializer = BanShopSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ShopService()
        try:
            data = service.ban_shop(shop_id, reason=serializer.validated_data.get('reason', ''))
        except ShopServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class AdminShopUnbanView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, shop_id):
        service = ShopService()
        try:
            data = service.unban_shop(shop_id)
        except ShopServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class VisitView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return error_response('请先登录', code=401, status=401)
        data = ShopService().list_user_visits(request.user)
        return success_response(data)

    def post(self, request):
        serializer = RecordVisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        service = ShopService()
        try:
            data = service.record_visit(user, serializer.validated_data['shop_id'])
        except ShopServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class ShopStatsView(APIView):
    permission_classes = [IsShopMerchant]

    def get(self, request):
        if not request.user.shop_id:
            return error_response('商家信息不存在', code=400)
        data = ShopService().get_shop_stats(request.user.shop_id)
        return success_response(data)


class AdminStatsView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        data = ShopService().get_admin_stats()
        return success_response(data)

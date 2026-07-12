from typing import Optional

from rest_framework.views import APIView

from apps.bikes.serializers import BikeWriteSerializer, ForceOffShelfSerializer
from apps.bikes.services.bike_service import BikeService, BikeServiceError
from apps.bikes.services.share_service import ShareService, ShareServiceError
from apps.common.permissions import IsPlatformAdmin, IsShopMerchant
from apps.common.response import error_response, success_response
from apps.shops.models import Shop


def _get_merchant_shop(user) -> Optional[Shop]:
    if not user.shop_id:
        return None
    return Shop.objects.filter(id=user.shop_id, is_deleted=False).first()


class BikeDetailView(APIView):
    def get(self, request, bike_id):
        shop_id_param = request.query_params.get('shop_id')
        try:
            shop_id = int(shop_id_param) if shop_id_param else None
        except (TypeError, ValueError):
            return error_response('无权查看该商家商品', code=403, status=403)
        service = BikeService()
        try:
            data = service.get_bike_detail(
                bike_id,
                shop_id=shop_id,
                timestamp=request.query_params.get('timestamp'),
                sign=request.query_params.get('sign'),
            )
        except BikeServiceError as exc:
            msg = str(exc)
            if '签名' in msg or '过期' in msg or '无权' in msg:
                code = 403
            else:
                code = 404
            return error_response(msg, code=code, status=code)
        return success_response(data)


class ShopBikeListCreateView(APIView):
    permission_classes = [IsShopMerchant]

    def get(self, request):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        status_param = request.query_params.get('status')
        status = int(status_param) if status_param else None
        data = BikeService().list_merchant_bikes(shop.id, status=status)
        return success_response(data)

    def post(self, request):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        serializer = BikeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = BikeService()
        try:
            data = service.create_bike(shop, serializer.validated_data)
        except BikeServiceError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class ShopBikeDetailView(APIView):
    permission_classes = [IsShopMerchant]

    def get(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        service = BikeService()
        try:
            data = service.get_merchant_bike(shop, bike_id)
        except BikeServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)

    def put(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        serializer = BikeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = BikeService()
        try:
            data = service.update_bike(shop, bike_id, serializer.validated_data)
        except BikeServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)

    def delete(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        service = BikeService()
        try:
            service.delete_bike(shop, bike_id)
        except BikeServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(None)


class ShopBikeOffShelfView(APIView):
    permission_classes = [IsShopMerchant]

    def post(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        service = BikeService()
        try:
            data = service.off_shelf_bike(shop, bike_id)
        except BikeServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class ShopBikeOnShelfView(APIView):
    permission_classes = [IsShopMerchant]

    def post(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        service = BikeService()
        try:
            data = service.on_shelf_bike(shop, bike_id)
        except BikeServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class ShopBikeMarkSoldView(APIView):
    permission_classes = [IsShopMerchant]

    def post(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        service = BikeService()
        try:
            data = service.mark_sold_bike(shop, bike_id)
        except BikeServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class ShopBikeShareLinkView(APIView):
    permission_classes = [IsShopMerchant]

    def post(self, request, bike_id):
        shop = _get_merchant_shop(request.user)
        if not shop:
            return error_response('商家信息不存在', code=400)
        try:
            data = ShareService().create_bike_share_link(shop, bike_id, request.user)
        except ShareServiceError as exc:
            code = 404 if '不存在' in str(exc) else 400
            return error_response(str(exc), code=code, status=code)
        return success_response(data)


class ResolveShareLinkView(APIView):
    def get(self, request, short_code):
        try:
            data = ShareService().resolve_short_code(short_code)
        except ShareServiceError as exc:
            msg = str(exc)
            code = 403 if ('签名' in msg or '过期' in msg) else 404
            return error_response(msg, code=code, status=code)
        return success_response(data)


class AdminBikeListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        data = BikeService().list_admin_bikes()
        return success_response(data)


class AdminBikeForceOffShelfView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, bike_id):
        serializer = ForceOffShelfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = BikeService()
        try:
            data = service.force_off_shelf(
                bike_id,
                request.user,
                reason=serializer.validated_data.get('reason', ''),
            )
        except BikeServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(data)


class AdminBikeRestoreView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, bike_id):
        service = BikeService()
        try:
            data = service.restore_bike(bike_id)
        except BikeServiceError as exc:
            return error_response(str(exc), code=400)
        return success_response(data)


class AdminBikeDeleteView(APIView):
    permission_classes = [IsPlatformAdmin]

    def delete(self, request, bike_id):
        service = BikeService()
        try:
            service.admin_delete_bike(bike_id)
        except BikeServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(None)

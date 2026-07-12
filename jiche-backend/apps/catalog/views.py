from rest_framework.views import APIView

from apps.catalog.models import Brand, BrandModel
from apps.common.response import error_response, success_response


class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.filter(is_enabled=True).order_by('sort_order', 'id')
        data = [{'id': b.id, 'name': b.name} for b in brands]
        return success_response(data)


class BrandModelsView(APIView):
    def get(self, request, brand_id):
        if not Brand.objects.filter(id=brand_id, is_enabled=True).exists():
            return error_response('品牌不存在', code=404, status=404)
        models = BrandModel.objects.filter(
            brand_id=brand_id,
            is_enabled=True,
        ).order_by('id')
        data = [m.name for m in models]
        return success_response(data)

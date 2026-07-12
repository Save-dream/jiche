from rest_framework import serializers
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticatedUser
from apps.common.response import error_response, success_response
from apps.favorites.services.favorite_service import FavoriteService, FavoriteServiceError


class AddFavoriteSerializer(serializers.Serializer):
    bike_id = serializers.IntegerField()


class FavoriteListCreateView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        data = FavoriteService().list_favorites(request.user)
        return success_response(data)

    def post(self, request):
        serializer = AddFavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = FavoriteService()
        try:
            data = service.add_favorite(request.user, serializer.validated_data['bike_id'])
        except FavoriteServiceError as exc:
            msg = str(exc)
            if msg == '已在收藏夹中':
                return error_response(msg, code=409, status=409)
            return error_response(msg, code=404, status=404)
        return success_response(data)


class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def delete(self, request, bike_id):
        service = FavoriteService()
        try:
            service.remove_favorite(request.user, bike_id)
        except FavoriteServiceError as exc:
            return error_response(str(exc), code=404, status=404)
        return success_response(None)

from rest_framework import serializers

from apps.accounts.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'nickname',
            'phone',
            'avatar',
            'is_staff',
            'is_super_staff',
            'shop_status',
            'shop_id',
        ]


class WxMiniLoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)


class LoginTicketConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128, required=False, allow_blank=True)
    mp_openid = serializers.CharField(max_length=64, required=False, allow_blank=True)
    unionid = serializers.CharField(max_length=64, required=False, allow_blank=True)
    web_openid = serializers.CharField(max_length=64, required=False, allow_blank=True)


class SimulateScanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)

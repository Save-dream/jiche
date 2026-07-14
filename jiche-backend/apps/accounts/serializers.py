from rest_framework import serializers

from apps.accounts.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    account_status = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'nickname',
            'phone',
            'avatar',
            'is_staff',
            'is_super_staff',
            'is_active',
            'is_deleted',
            'account_status',
            'shop_status',
            'shop_id',
            'ban_reason',
            'banned_at',
            'delete_reason',
            'deleted_at',
            'created_at',
        ]


class ReasonActionSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, trim_whitespace=True)

    def validate_reason(self, value):
        value = (value or '').strip()
        if len(value) < 2:
            raise serializers.ValidationError('请填写操作理由（至少 2 个字）')
        return value


class WxMiniLoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)


class LoginTicketConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128, required=False, allow_blank=True)
    mp_openid = serializers.CharField(max_length=64, required=False, allow_blank=True)
    unionid = serializers.CharField(max_length=64, required=False, allow_blank=True)
    web_openid = serializers.CharField(max_length=64, required=False, allow_blank=True)


class SimulateScanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

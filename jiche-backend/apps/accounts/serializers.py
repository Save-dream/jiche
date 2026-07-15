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
            'last_login_at',
            'last_login_platform',
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


class PasswordRegisterSerializer(serializers.Serializer):
    """临时账号注册（微信未接通时模拟授权注册）。"""

    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    nickname = serializers.CharField(max_length=64, required=False, allow_blank=True, default='')
    phone = serializers.CharField(max_length=11, required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value):
        value = (value or '').strip()
        if len(value) < 2:
            raise serializers.ValidationError('账号至少 2 个字符')
        if User.objects.filter(internal_username=value, is_deleted=False).exists():
            raise serializers.ValidationError('账号已存在')
        return value

    def validate_phone(self, value):
        value = (value or '').strip()
        if not value:
            return None
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validate_nickname(self, value):
        value = (value or '').strip()
        return value[:64] if value else ''


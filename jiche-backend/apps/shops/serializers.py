import re

from rest_framework import serializers

from apps.shops.models import ShopApplication
from apps.shops.services.application_service import LABEL_TO_SHOP_TYPE


class ShopApplicationSubmitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)
    shop_type = serializers.CharField(max_length=16)
    contact_name = serializers.CharField(max_length=32)
    phone = serializers.CharField(max_length=11)
    address = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    main_models = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    description = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    wechat_qrcode = serializers.CharField(max_length=512)
    qualification_photo = serializers.CharField(max_length=512, required=False, allow_blank=True, allow_null=True)

    def validate_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('请填写商家名称')
        if len(value) < 2:
            raise serializers.ValidationError('商家名称至少 2 个字')
        return value

    def validate_shop_type(self, value):
        if value not in LABEL_TO_SHOP_TYPE and value not in ('1', '2', 1, 2):
            raise serializers.ValidationError('请选择入驻类型')
        return value

    def validate_contact_name(self, value):
        if not re.match(r'^[\u4e00-\u9fa5]{2,10}$', value):
            raise serializers.ValidationError('姓名须为2-10位中文')
        return value

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请填写正确的手机号')
        return value


class ShopApplicationAuditSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('reject_reason'):
            raise serializers.ValidationError({'reject_reason': '请填写驳回原因'})
        return attrs


class ShopProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, required=False)
    contact_name = serializers.CharField(max_length=32, required=False)
    phone = serializers.CharField(max_length=11, required=False)
    address = serializers.CharField(max_length=100, required=False, allow_blank=True)
    main_models = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(max_length=200, required=False, allow_blank=True)
    avatar = serializers.CharField(max_length=512, required=False, allow_blank=True, allow_null=True)
    wechat_qrcode = serializers.CharField(max_length=512, required=False, allow_blank=True)
    qualification_photo = serializers.CharField(max_length=512, required=False, allow_blank=True, allow_null=True)


class RecordVisitSerializer(serializers.Serializer):
    shop_id = serializers.IntegerField()


class BanShopSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, default='', allow_blank=True)

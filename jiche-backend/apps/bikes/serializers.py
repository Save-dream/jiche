from decimal import Decimal

from rest_framework import serializers


class BikeWriteSerializer(serializers.Serializer):
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    brand = serializers.CharField(max_length=32)
    model = serializers.CharField(max_length=64)
    year = serializers.IntegerField(min_value=1980, max_value=2100)
    register_date = serializers.DateField(required=False, allow_null=True)
    displacement = serializers.CharField(max_length=16)
    mileage = serializers.IntegerField()
    transfer_count = serializers.IntegerField(min_value=0, max_value=99)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    can_transfer = serializers.BooleanField(required=False, default=True)
    negotiable = serializers.BooleanField(required=False, default=True)

    def validate_mileage(self, value):
        if value is None or value <= 1:
            raise serializers.ValidationError('行驶里程须大于 1')
        return value

    def validate_price(self, value):
        if value is None or Decimal(value) <= 1:
            raise serializers.ValidationError('售价须大于 1')
        return value

    def validate_transfer_count(self, value):
        if value is None:
            raise serializers.ValidationError('请填写过户次数，可为 0')
        return value
    engine_status = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    suspension_status = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    brake_status = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    electrical_status = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    frame_status = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    modification = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    defects = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    maintenance = serializers.CharField(max_length=500, required=False, default='', allow_blank=True)
    delivery_method = serializers.CharField(max_length=64, required=False, default='', allow_blank=True)
    fee_note = serializers.CharField(max_length=200, required=False, default='', allow_blank=True)
    after_sale = serializers.CharField(max_length=200, required=False, default='', allow_blank=True)
    cover_image = serializers.CharField(max_length=512, required=False, allow_blank=True)
    images = serializers.ListField(
        child=serializers.CharField(max_length=512),
        required=False,
        default=list,
    )
    condition_images = serializers.ListField(
        child=serializers.CharField(max_length=512),
        required=False,
        default=list,
    )


class ForceOffShelfSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, default='', allow_blank=True)

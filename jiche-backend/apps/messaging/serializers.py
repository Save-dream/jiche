from rest_framework import serializers


class CreateThreadSerializer(serializers.Serializer):
    bike_id = serializers.IntegerField()
    content = serializers.CharField(max_length=500)
    contact_phone = serializers.CharField(max_length=11, required=False, default='', allow_blank=True)


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)
    sender_type = serializers.IntegerField(min_value=1, max_value=3)


class MarkReadSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'shop'])

from rest_framework import serializers

class DummyDetailSerializer(serializers.Serializer):
    status = serializers.IntegerField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()

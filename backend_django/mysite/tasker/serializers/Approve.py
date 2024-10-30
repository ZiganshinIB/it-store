from rest_framework import serializers
from ..models import Approve

class ApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approve
        fields = ['id', 'title', 'description', 'group', 'order_number', 'status', 'on_request']


from rest_framework import serializers
from .models import Product_rags as Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

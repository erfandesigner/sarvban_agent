import datetime, hashlib, json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Product_rags as Product
from .serializers import ProductSerializer
from .embedding import embed_text
from .rag import answer


class IngestView(APIView):
    def post(self, request):
        data = request.data
        obj = Product.objects.create(
            title       = data["title"],
            description = data.get("description",""),
            cat_path    = data.get("catPath", []),
            address     = data.get("address", {}),
            price       = data.get("price", {}),
            export      = data.get("export", {}),
            properties  = data.get("info", []),
            # created_at  = datetime.datetime.fromtimestamp(data["createdAt"]["0"]),
        )
        text = f"title: {obj.title}\\ndesc: {obj.description}"
        obj.embedding = embed_text(text)
        obj.save()
        return Response({"id": obj.id})

class AnswerView(APIView):
    def post(self, request):
        q = request.data.get("query","")
        f = request.data.get("filters",{})
        return Response(answer(q, f))

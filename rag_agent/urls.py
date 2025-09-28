from django.urls import path
from .views import IngestView, AnswerView

urlpatterns = [
    path("ingest/", IngestView.as_view(), name="ingest"),
    path("answer/", AnswerView.as_view(), name="answer"),
]

from django.db import models
from pgvector.fields import VectorField

class Product(models.Model):
    # your core schema fields
    title        = models.TextField()
    description  = models.TextField(blank=True)
    cat_path     = models.JSONField(default=list)
    address      = models.JSONField(default=dict)
    price        = models.JSONField(default=dict)
    export       = models.JSONField(default=dict)
    properties   = models.JSONField(default=dict)
    created_at   = models.DateTimeField()
    # vector embedding
    embedding    = VectorField(dimensions=1536)

    def __str__(self):
        return self.title

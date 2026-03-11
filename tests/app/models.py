from django.db import models

from namedid import NamedIDField, add_namedid


class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    created_date = models.DateField()

    named_id = NamedIDField(
        source_fields=["name", "code", "created_date"],
        max_length=200,
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return self.name


@add_namedid(named_id=["title", "id"], slug=["title", "category"])
class Article(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    content = models.TextField()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self) -> str:
        return self.title

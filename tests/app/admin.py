from django.contrib import admin

from .models import Article, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_date", "named_id", "named_id_custom")
    readonly_fields = ("named_id", "named_id_custom")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "named_id", "slug")
    readonly_fields = ("named_id", "slug")

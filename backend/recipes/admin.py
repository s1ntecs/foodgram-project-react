from django.contrib.admin import ModelAdmin, register

from .models import (Favorite, Ingredient, Product, Recipe, ShoppingCart,
                     Subscribe, Tag)

EMPTY = '-пусто-'


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name', 'slug',)
    ordering = ('color',)
    empty_value_display = EMPTY


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('measurement_unit',)
    empty_value_display = EMPTY


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'added_in_favorites')
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('added_in_favorites',)
    empty_value_display = EMPTY

    def added_in_favorites(self, obj):
        return obj.favorite_recipe.count()


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'id', 'product_id', 'amount'
    )
    list_filter = ('product_id__name',)
    ordering = ('product_id',)
    empty_value_display = EMPTY


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    empty_value_display = EMPTY


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    list_display = ('user', 'author',)
    list_filter = ('user', 'author',)
    empty_value_display = EMPTY


@register(ShoppingCart)
class ShopCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    empty_value_display = EMPTY

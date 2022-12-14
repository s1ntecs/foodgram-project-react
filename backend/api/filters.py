from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from rest_framework.exceptions import ValidationError

from recipes.models import Recipe, Tag
User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta():
        model = Recipe
        fields = ['tags']

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            raise ValidationError(
                {"Вы должны авторизоваться, чтобы видеть избранные рецепты"}
            )
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset.all().exclude(favorite_recipe__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            raise ValidationError(
                {"Вы должны авторизоваться, чтобы видеть список покупок"}
            )
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset.all().exclude(shopping_cart__user=self.request.user)

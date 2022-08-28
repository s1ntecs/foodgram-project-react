from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Product, Recipe, Tag, TagsRecipe


def get_recipe(recipe_id):
    """ Получает id рецепта и отдает рецепт"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        raise ValidationError(
            {"errors": "velit"}
        )
    return recipe


def get_recipe_ingredients_txt(shop_cart):
    """ Создает список покупок основанный
        из списка рецептов вашей корзины """
    text = "Ингредиенты: \n"
    ingredients_dict = {}
    for cart in shop_cart:
        recipe = Recipe.objects.get(id=cart.recipe.id)
        ingredients = Ingredient.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            if ingredient.product_id in ingredients_dict:
                ingredients_dict[ingredient.product_id] += ingredient.amount
            else:
                ingredients_dict[ingredient.product_id] = ingredient.amount
    for product in ingredients_dict:
        product_ = ingredients_dict[product]
        text += (
            f"{product.name} - {str(product_)} {product.measurement_unit}. \n")
    return text


def create_tags(tags_id, recipe):
    """ Создаем тэги для рецепта"""
    for tag_id in tags_id:
        try:
            tag = Tag.objects.get(id=tag_id)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        tag = TagsRecipe.objects.create(
                tag=tag, recipe=recipe)


def create_ingredients(ingredients_data, recipe):
    """ Создаем ингредиенты для рецепта"""
    for cur_data in ingredients_data:
        product_id = cur_data['id']
        amount = cur_data['amount']
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        Ingredient.objects.create(
            product_id=product, recipe=recipe, amount=amount)

from recipes.models import Ingredient, Product, Recipe


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


def create_ingredients_amount(self, ingredients_data, recipe):
    Ingredient.objects.bulk_create(
            [Ingredient(
                product_id=Product.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients_data]
        )

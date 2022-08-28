from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.services import create_ingredients, create_tags
from recipes.models import (Favorite, Ingredient, Product, Recipe,
                            ShoppingCart, Subscribe, Tag, TagsRecipe)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, instance):
        request_user = self.context.get('request').user.id
        try:
            Subscribe.objects.get(
                user=request_user,
                author=instance.id
            )
        except Subscribe.DoesNotExist:
            return False
        return True

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed')


class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.SerializerMethodField()
    current_password = serializers.SerializerMethodField()

    def get_new_password(self, obj):
        return obj

    def get_current_password(self, obj):
        return obj

    def validate(self, data):
        data = self.initial_data
        me = data.pop('user')
        if data['current_password'] != me.password:
            raise ValidationError(
                {"Wrong current password"}
            )
        if data['current_password'] == data['new_password']:
            raise ValidationError(
                {"The current and new password cannot be the same"}
            )
        try:
            validate_password(data['new_password'], me)
        except exceptions.ValidationError:
            raise ValidationError(
                "This psssassword is too short."
                "It must contain at least 8 characters."
                "This password is too common."
                "This password is entirely numeric"
            )
        return data

    class Meta:
        model = User
        fields = ('new_password', 'current_password')


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('password', 'username', 'email',
                  'first_name', 'last_name', 'id')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" как имя пользователя.')
        return value


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('name', 'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def get_id(self, obj):
        return obj.product_id.id

    def get_name(self, obj):
        return obj.product_id.name

    def get_measurement_unit(self, obj):
        return obj.product_id.measurement_unit


class DownloadShoppingCartViewSet(serializers.ModelSerializer):
    ingredient = serializers.FileField(
        allow_empty_file=True,
        use_url='static/'
    )

    class Meta:
        model = Ingredient
        fields = ('ingredient')


class IngredientSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('product_id', 'amount')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        extra_kwargs = {'color': {'required': True}}


class TagsRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    tag = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TagsRecipe
        fields = ('id', 'recipe', 'tag')


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(
        read_only=True,
        many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, instance):
        recipe = instance
        queryset = recipe.recipe_ingredient.all()
        return IngredientListSerializer(queryset, many=True).data

    def get_is_favorited(self, instance):
        request_user = self.context.get('request').user.id
        try:
            Favorite.objects.get(
                user=request_user,
                recipe=instance.id
            )
        except Favorite.DoesNotExist:
            return False
        return True

    def get_is_in_shopping_cart(self, instance):
        request_user = self.context.get('request').user.id
        try:
            ShoppingCart.objects.get(
                user=request_user,
                recipe=instance.id
            )
        except ShoppingCart.DoesNotExist:
            return False
        return True

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'tags',
                  'ingredients', 'cooking_time')


class RecipesListSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(
        read_only=True,
        many=True
    )
    ingredients = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, instance):
        recipe = instance
        queryset = recipe.recipe_ingredient.all()
        return IngredientListSerializer(queryset, many=True).data

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'tags',
                  'ingredients', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        required=True,
        max_length=None,
        use_url=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    ingredients = IngredientListSerializer(
        many=True,
        required=True)
    tags = TagsSerializer(
        many=True,
        read_only=True
    )

    def validate(self, data):
        try:
            self.initial_data['ingredients']
            tags = self.initial_data['tags']
        except KeyError:
            raise ValidationError(
                {"errors": "Поле tags, ingredients являются обязательными"}
            )
        if tags:
            return data
        else:
            raise ValidationError(
                {"errors": "укажите тэги"}
            )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(
            instance, context=context).data

    def get_tags(self, instance):
        tags_id = self.initial_data['tags']
        return tags_id

    def create(self, request):
        ingredients_data = request.pop('ingredients')
        tags_id = request.pop('tags')
        recipe = Recipe.objects.create(**request)
        create_tags(
            tags_id,
            recipe
        )
        create_ingredients(
            ingredients_data,
            recipe
        )
        return recipe

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')


class RecipesShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    recipes = RecipesShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

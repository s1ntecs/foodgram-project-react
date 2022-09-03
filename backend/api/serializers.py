import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.services import create_ingredients_amount
from recipes.models import (Favorite, Ingredient, Product, Recipe,
                            ShoppingCart, Subscribe, Tag)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, instance):
        if not self.context:
            return False
        request_user = not self.context.get('request').user.id
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
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='Email',
        write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)
    token = serializers.CharField(
        label='Токен',
        read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if not authenticate(username=user.username, password=password):
                    raise serializers.ValidationError(
                        'Вы не указали пользователя',
                        code='authorization')
            else:
                raise serializers.ValidationError(
                        'Пользователя с таким email нет',
                        code='authorization')
        else:
            msg = 'Необходимо указать "адрес электронной почты" и "пароль".'
            raise serializers.ValidationError(
                msg,
                code='authorization')
        attrs['user'] = user
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',)

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.username,
                password=current_password):
            raise serializers.ValidationError(
                "Не удается авторизоваться", code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class SubscribeSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data['user'] == data['author']:
            raise ValidationError("You can not subscribe yourself")
        return data

    class Meta:
        model = Subscribe
        fields = ('user', 'author')


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


class IngredientsEditSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ('id', 'amount')


class DownloadShoppingCartViewSet(serializers.ModelSerializer):
    ingredient = serializers.FileField(
        allow_empty_file=True,
        use_url='static/'
    )

    class Meta:
        model = Ingredient
        fields = ('ingredient')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


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
        return Favorite.objects.filter(user=request_user, recipe=instance.id)

    def get_is_in_shopping_cart(self, instance):
        request_user = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=request_user, recipe=instance.id).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'tags',
                  'ingredients', 'cooking_time')


class OneRecipeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
    ingredients = IngredientsEditSerializer(
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())

    def validate_ingredients(self, value):
        try:
            ingredients = self.initial_data.get('ingredients')
        except KeyError:
            raise ValidationError(
                {"errors": "Поле ingredients являются обязательными"}
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов >= 1')
        return ingredients

    def validate_tags(self, value):
        try:
            tags = self.initial_data.get('tags')
        except KeyError:
            raise ValidationError(
                {"errors": "Поле tags являются обязательными"}
            )
        return tags

    def validate_cooking_time(self, value):
        cooking_time = value
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1')
        return cooking_time

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(
            instance, context=context).data

    def create(self, request):
        author = self.context.get('request').user
        ingredients_data = request.pop('ingredients')
        tags_id = request.pop('tags')
        recipe = Recipe.objects.create(author=author, **request)
        recipe.tags.set(tags_id)
        create_ingredients_amount(self, ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            create_ingredients_amount(self, ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        return instance

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

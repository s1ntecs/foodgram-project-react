from api.filters import IngredientFilter, RecipeFilter
from api.paginators import SubscribtionPagintation
from api.services import (create_ingredients, create_tags, get_recipe,
                          get_recipe_ingredients_txt)
# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Product, Recipe,
                            ShoppingCart, Subscribe, Tag, TagsRecipe)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.functions import create_access_token
from users.models import User
from users.serializers import AuthSerializer

from .permissions import (AdminOrReadOnly, Authenticated,
                          AuthorOrAuthenticated, Unauthorized)
from .serializers import (IngredientListSerializer, IngredientSerializer,
                          ProductSerializer, RecipeListSerializer,
                          RecipeSerializer, RecipesListSerializer,
                          SetPasswordSerializer, SignUpSerializer,
                          SubscriptionsSerializer, TagsSerializer,
                          UserSerializer)


class FavoriteViewSet(viewsets.ViewSet):

    permission_classes = [Authenticated]

    def create(self, request, recipe_id):
        recipe = get_recipe(recipe_id)
        try:
            Favorite.objects.create(recipe=recipe, user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"errors": "Рецпт уже в избранных"}
            )
        serializer = RecipesListSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, recipe_id):
        recipe = get_recipe(recipe_id)
        user = self.request.user
        try:
            favorite = Favorite.objects.get(recipe=recipe, user=user)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ViewSet):

    permission_classes = [Authenticated]

    def create(self, request, author_id):
        try:
            author = User.objects.get(id=author_id)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        if request.user == author:
            raise ValidationError("You can not subscribe yourself")
        try:
            Subscribe.objects.create(author=author, user=request.user)
        except IntegrityError:
            raise ValidationError(
                {"errors": "Вы уже подписаны на автора"}
            )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        try:
            author = User.objects.get(id=author_id)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        try:
            subscribe = Subscribe.objects.get(author=author, user=request.user)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ViewSet):

    permission_classes = [Authenticated]

    def create(self, request, recipe_id):
        recipe = get_recipe(recipe_id)
        try:
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"errors": "Вы уже добавили рецепт в корзину"}
            )
        serializer = RecipesListSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, recipe_id):
        recipe = get_recipe(recipe_id)
        user = self.request.user
        try:
            favorite = ShoppingCart.objects.get(recipe=recipe, user=user)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [Authenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.OrderingFilter, ]
    ordering = ['-id']


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, ]
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):

    queryset = Ingredient.objects.all()
    permission_classes = [Authenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientListSerializer
        return IngredientSerializer


class SubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionsSerializer
    permission_classes = [Authenticated]
    pagination_class = None

    def get_queryset(self):
        me = self.request.user
        user_subscriptions = User.objects.filter(follow__user=me)
        return user_subscriptions


class RecipeViewSet(viewsets.ModelViewSet):

    permission_classes = [AuthorOrAuthenticated]
    lookup_field = 'name'
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ['name']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipesListSerializer
        elif self.action == 'retrieve':
            return RecipeListSerializer
        return RecipeSerializer

    def get_queryset(self):
        recipe = Recipe.objects.all()
        return recipe

    def get_object(self):
        recipe_id = self.kwargs.get('name')
        recipe = get_recipe(recipe_id)
        return recipe

    def perform_create(self, serializer):
        author = self.request.user
        in_data = serializer.initial_data
        serializer.save(
            author=author,
            ingredients=in_data['ingredients'],
            tags=in_data['tags']
            )

    def perform_update(self, serializer):
        recipe_id = self.kwargs.get('name')
        in_data = serializer.initial_data
        serializer.validated_data.pop('ingredients', 'tags')
        serializer.is_valid(raise_exception=True)
        Recipe.objects.filter(id=recipe_id).update(**serializer.validated_data)
        recipe = get_recipe(recipe_id)
        tags_id = in_data['tags']
        tags = TagsRecipe.objects.filter(recipe=recipe)
        tags.delete()
        create_tags(tags_id, recipe)
        ingredients = Ingredient.objects.filter(recipe=recipe)
        ingredients.delete()
        ingredients_data = in_data['ingredients']
        create_ingredients(ingredients_data, recipe)
        serializer = RecipeListSerializer(recipe)
        return serializer


class DownloadShoppingCartViewSet(viewsets.ViewSet):

    def list(self, request):
        author = self.request.user
        shop_cart = ShoppingCart.objects.filter(user=author.id)
        text = get_recipe_ingredients_txt(shop_cart)
        filename = "my-file.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename))
        return response


class BlacklistRefreshView(APIView):

    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Success")


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    lookup_field = 'username'
    pagination_class = SubscribtionPagintation
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    ordering = ['username']
    search_fields = ['username']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'retrieve':
            return SignUpSerializer
        return SignUpSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(**serializer.validated_data)
        user.save()
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            url_path=r'set_password',
            permission_classes=(IsAuthenticated,))
    def set_password(self, request, format=None):
        me = self.request.user
        data = self.request.data.copy()
        data['user'] = me
        serializer = SetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        me.password = data['new_password']
        me.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['post'],
            url_path=r'token/login',
            permission_classes=(Unauthorized,))
    def login(self, request, format=None):
        data = self.request.data.copy()
        serializer = AuthSerializer(data=data)
        id_data = serializer.initial_data
        email = id_data['email']
        password = id_data['password']
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        if user.password != password:
            data = {'error': 'wrong password'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user.confirmation_code = ''
        user.save()
        token = create_access_token(user)
        return Response(token)

    @action(detail=False,
            methods=('get', 'patch'),
            url_path=r'me',
            permission_classes=(IsAuthenticated,))
    def me(self, request, format=None):
        me = self.request.user

        if request.method == 'GET':
            serializer = UserSerializer(me)
            return Response(serializer.data)

        data = self.request.data.copy()
        data.pop('role', None)
        data['email'] = me.email
        data['username'] = me.username
        serializer = UserSerializer(me, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'subscriptions',
    )
    def subscriptions(self, request):
        user_subscriptions = User.objects.filter(follow__user=request.user)
        page = self.paginate_queryset(user_subscriptions)
        serializer = SubscriptionsSerializer(
            page,
            context=self.get_serializer_context(),
            many=True
        )
        return self.get_paginated_response(serializer.data)

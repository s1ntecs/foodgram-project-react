from djoser.views import UserViewSet

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from recipes.models import (Favorite, Product, Recipe,
                            ShoppingCart, Subscribe, Tag)
from .filters import IngredientFilter, RecipeFilter
from .paginators import SubscribtionPagintation
from .permissions import AdminOrReadOnly, AuthorOrAuthenticated
from .serializers import (OneRecipeListSerializer, ProductSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagsSerializer, TokenSerializer,
                          UserCreateSerializer, UserPasswordSerializer,
                          UserSerializer)
from .services import get_recipe_ingredients_txt


class FavoriteViewSet(viewsets.ViewSet):
    """ Избранные рецепты."""

    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(
                recipe=recipe, user=self.request.user).exists():
            raise ValidationError(
                {"errors": "Рецeпт уже в избранных"}
            )
        Favorite.objects.create(recipe=recipe, user=self.request.user)
        serializer = OneRecipeListSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
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
    """ Подписки на авторов."""

    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer

    def create(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        data = self.request.data.copy()
        data['user'] = request.user.id
        data['author'] = author.id
        serializer = SubscribeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        if Subscribe.objects.filter(author=author, user=request.user).exists():
            raise ValidationError(
                {"errors": "Вы уже подписаны на автора"}
            )
        Subscribe.objects.create(author=author, user=request.user)
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
    """ Список покупок."""

    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"errors": "Вы уже добавили рецепт в корзину"}
            )
        serializer = OneRecipeListSerializer(recipe)
        return Response(serializer.data)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.request.user
        try:
            favorite = ShoppingCart.objects.get(recipe=recipe, user=user)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"errors": "velit"}
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ModelViewSet):
    """Список тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AdminOrReadOnly]
    pagination_class = None


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ Продукты."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, ]
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ Создаем рецепты."""

    permission_classes = [AuthorOrAuthenticated]
    lookup_field = 'name'
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ['name']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action == SAFE_METHODS:
            return RecipeListSerializer
        return RecipeSerializer

    def get_queryset(self):
        recipe = Recipe.objects.all()
        return recipe

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_object(self):
        recipe_id = self.kwargs.get('name')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return recipe


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


class UsersViewSet(UserViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    lookup_field = 'username'
    pagination_class = SubscribtionPagintation
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    ordering = ['username']
    search_fields = ['username']

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserSerializer

    def get_object(self):
        id = self.kwargs.get('username')
        user = get_object_or_404(User, id=id)
        return user

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'subscriptions',
    )
    def subscriptions(self, request):
        """Ваши подписки."""

        user_subscriptions = User.objects.filter(follow__user=request.user)
        page = self.paginate_queryset(user_subscriptions)
        serializer = SubscriptionsSerializer(
            page,
            context=self.get_serializer_context(),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=('get',),
            url_path=r'me',
            permission_classes=(IsAuthenticated,),
            serializer_class=(UserSerializer,))
    def me(self, request, format=None):
        me = self.request.user
        serializer = UserSerializer(me)
        return Response(serializer.data)


class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED)


@api_view(['post'])
def set_password(request):
    """Изменить пароль."""

    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request})
    serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введите верные данные!'},
        status=status.HTTP_400_BAD_REQUEST)

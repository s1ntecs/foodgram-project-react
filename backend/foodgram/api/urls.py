from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from .views import (BlacklistRefreshView, DownloadShoppingCartViewSet,
                    FavoriteViewSet, IngredientViewSet, ProductViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscribeViewSet,
                    TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    r'users/(?P<author_id>\d+)/subscribe',
    SubscribeViewSet, basename='SubscribeList'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet, basename='FavoriteList'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet, basename='ShoppingCartList'
)
router.register(
    r'recipes/download_shopping_cart',
    DownloadShoppingCartViewSet, basename='DownloadShoppingCart'
)
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredient', IngredientViewSet, basename='ingredients')
router.register(r'ingredients', ProductViewSet, basename='products')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserViewSet)
router.register(r'auth', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/token/logout/', BlacklistRefreshView.as_view(), name='logout'),
]

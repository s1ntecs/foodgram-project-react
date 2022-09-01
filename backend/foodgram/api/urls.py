from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from .views import (AuthToken, DownloadShoppingCartViewSet, 
                    ProductViewSet, RecipeViewSet, FavoriteViewSet,
                    ShoppingCartViewSet, SubscribeViewSet, TagViewSet,
                    UsersViewSet, set_password)

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
router.register(r'ingredients', ProductViewSet, basename='products')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UsersViewSet)

urlpatterns = [
    path(
        'auth/token/login/',
        AuthToken.as_view(),
        name='login'),
    path(
        'users/set_password/',
        set_password,
        name='set_password'),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

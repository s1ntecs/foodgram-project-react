from colorfield.fields import ColorField

from django.core import validators
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название продукта',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения',
    )

    def __str__(self):
        return str(self.name)


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Подписаться'
    )

    class Meta:
        constraints = [UniqueConstraint(
            fields=['user', 'author'],
            name='unique_subscribe',
        )]

    def __str__(self):
        return f'{self.author} {self.user}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название тэга',
    )
    color = ColorField()
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Подписчик'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='название продукта',
    )
    image = models.ImageField(
        upload_to='media/image/',
        blank=True
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Product,
        through='Ingredient',
        verbose_name="Ингредиенты",
        related_name='recipe_ingredients',
        blank=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name='recipe_tags')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в мин.',
        validators=[validators.MinValueValidator(
            1, message='Время приготовления должно быть больше 1 мин.'), ])

    def __str__(self):
        return str(self.name)


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='recipe_ingredient',
    )
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='id продукта',
        related_name='product_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Минимальное количество ингридиентов 1'),),
        verbose_name='Количество',
    )

    def __str__(self):
        return str(self.product_id)


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранное'
    )

    class Meta:
        constraints = [UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
        )]

    def __str__(self):
        return self.recipe


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Корзина'
    )

    class Meta:
        constraints = [UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
        )]

    def __str__(self):
        return self.recipe

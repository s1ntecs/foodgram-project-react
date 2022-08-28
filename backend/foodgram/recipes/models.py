# Create your models here.
from colorfield.fields import ColorField
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
        upload_to='static/image/',
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
        through='TagsRecipe',
        verbose_name="Тэги",
        related_name='recipe_tags')
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


class TagsRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='recipe_tag',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тэги',
        related_name='tags_recipe',
    )

    def __str__(self):
        return self.tag


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
    amount = models.IntegerField()

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

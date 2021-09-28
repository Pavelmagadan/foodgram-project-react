from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_Ingredient'
            ),
        ]

    def __str__(self):
        return ', '.join((self.name, self.measurement_unit))


class Tags(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Имя')
    color = models.CharField(max_length=10, unique=True, verbose_name='Цвет')
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    tags = models.ManyToManyField(
        Tags, related_name='recipes', verbose_name='Тег'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes_images/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления, мин',
        validators=[MinValueValidator(
            1, 'Время приготовления должно быть положительным числом'
        )]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.FloatField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            0.001, 'Количество ингредианта должно быть положительным числом'
        )]
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_IngredientRecipe'
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписчик'
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed'],
                name='unique_subscription'
            ),
        ]


class Favorite(models.Model):
    lover = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='lovers',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['lover', 'recipe'],
                name='unique_Favorite'
            ),
        ]


class ShopingCart(models.Model):
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_cart',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='buyer',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name_plural = 'Рецепты в корзине'

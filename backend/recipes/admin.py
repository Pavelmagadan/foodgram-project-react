from django.contrib import admin

from .models import (
    Favorite, Ingredients, Recipes, ShopingCart, Subscription, Tags,
)


class IngredientInline(admin.TabularInline):
    model = Ingredients.recipes.through
    extra = 1


class TagInline(admin.TabularInline):
    model = Tags.recipes.through
    extra = 1


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'subscribed',)
    ordering = ('subscriber',)
    list_display_links = ('id', 'subscriber', 'subscribed',)

@admin.register(ShopingCart)
class ShopingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'recipe',)
    ordering = ('buyer',)
    list_display_links = ('id', 'buyer', 'recipe',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'lover', 'recipe',)
    ordering = ('lover',)
    list_display_links = ('id', 'lover', 'recipe',)


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    ordering = ('name',)
    list_display_links = ('id', 'name', 'color', 'slug',)


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline, TagInline]
    list_display = (
        'id', 'author', 'name', 'text', 'cooking_time', 'in_favorite'
    )
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('name', 'author__username',)
    list_display_links = (
        'id', 'author', 'name', 'text', 'cooking_time', 'in_favorite',
    )
    ordering = ('name',)
    exclude = ('tags',)

    def in_favorite(self, obj):
        return obj.lovers.count()

    in_favorite.short_description = 'В избранном'


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'measurement_unit',)
    ordering = ('name',)

import webcolors
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import IngredientRecipe, Ingredients, Recipes, Tags

User = get_user_model()

class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.normalize_hex(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredients.objects.all()
    )
    name = serializers.StringRelatedField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(source='lovers')
    is_in_shopping_cart = serializers.SerializerMethodField(source='buyer')
    tags = TagsSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set', many=True
    )

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipes

    def get_is_favorited(self, obj):
        user = self.context['request'].user.username
        lover = obj.lovers.filter(lover__username=user)
        return lover.exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user.username
        buyer = obj.buyer.filter(buyer__username=user)
        return buyer.exists()


class PartialRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = Recipes


class RecipesCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set', many=True
    )
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        fields = (
            'id',
            'ingredients',
            'author',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipes

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.tags.set(tags)
        instance.ingredientrecipe_set.all().delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
        return instance


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(source='recipe')

    class Meta():
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, _):
        return True

    def get_recipes(self, obj):
        limit = 10
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            limit = int(recipes_limit)
        queryset = obj.recipe.all()[:limit]
        serializer = PartialRecipesSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipe.all().count()

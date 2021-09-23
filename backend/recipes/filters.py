import django_filters

from django_filters import rest_framework as filters

from recipes.models import Recipes, Tags


class RecipesFilter(filters.FilterSet):

    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all()
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author']

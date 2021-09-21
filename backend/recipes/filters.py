from django_filters import rest_framework as filters

from recipes.models import Recipes


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipesFilter(filters.FilterSet):
    tags = CharFilterInFilter(field_name='tags__name', lookup_expr='in')

    class Meta:
        model = Recipes
        fields = ['tags', 'author']

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CreateDeleteFavoriteView, CreateDeleteInCartView,
                    CreateDeleteSubscriptionView, IngredientsViewSet,
                    ListSubscriptionsAPIView, RecipesListRetreveDestroyView,
                    TagsViewSet, download_shoping_cart)

router = DefaultRouter()
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register(
    'recipes', RecipesListRetreveDestroyView, basename='get_recipes'
)


urlpatterns = [
    path('recipes/<id>/favorite/', CreateDeleteFavoriteView.as_view()),
    path('recipes/<id>/shopping_cart/', CreateDeleteInCartView.as_view()),
    path('users/subscriptions/', ListSubscriptionsAPIView.as_view()),
    path('users/<id>/subscribe/', CreateDeleteSubscriptionView.as_view()),
    path('recipes/download_shopping_cart/', download_shoping_cart),
    path('', include(router.urls)),
]

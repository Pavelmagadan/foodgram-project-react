from os import path

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram import settings

from .filters import RecipesFilter
from .models import (
    Favorite, Ingredients, Recipes, ShopingCart, Subscription, Tags,
)
from .permissions import IsOwnerOrSafeMethodOnly
from .serializers import (
    IngredientsSerializer, PartialRecipesSerializer, RecipesCreateSerializer,
    RecipesSerializer, SubscriptionsSerializer, TagsSerializer,
)

User = get_user_model()


class RecipesListRetreveDestroyView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin
):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    create_serializer_class = RecipesCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    permission_classes = [IsOwnerOrSafeMethodOnly]

    def get_queryset(self):
        query_params = self.request.query_params
        exclude_params = {}
        filter_params = {}
        username = self.request.user.username
        if query_params.get('is_favorited') == 'false':
            exclude_params['lovers__lover__username'] = username
        elif query_params.get('is_favorited') == 'true':
            filter_params['lovers__lover__username'] = username
        if query_params.get('is_in_shopping_cart') == 'false':
            exclude_params['buyer__buyer__username'] = username
        elif query_params.get('is_in_shopping_cart') == 'true':
            filter_params['buyer__buyer__username'] = username
        return Recipes.objects.filter(**filter_params).exclude(
            **exclude_params
        )

    def perform_create(self, serializer):
        new = serializer.save(author=self.request.user)
        print(new.id)

    def get_create_serializer(self, *args, **kwargs):
        serializer_class = self.create_serializer_class
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_create_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        self.perform_create(create_serializer)
        headers = self.get_success_headers(create_serializer.data)
        try:
            new_recipe = Recipes.objects.get(id=create_serializer.data['id'])
        except IndexError:
            pass
        serializer = self.get_serializer(new_recipe)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_create_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        view_serializer = self.get_serializer(instance)
        return Response(view_serializer.data)


class ListSubscriptionsAPIView(generics.ListAPIView):
    serializer_class = SubscriptionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            subscribers__subscriber=self.request.user
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class CreateDeleteRelationView(APIView):
    model = None
    connecting_model = None
    serializer_class = None
    user_related_field = None
    model_related_field = None

    def get_kwargs(self, user, object):
        return {
            self.user_related_field: user,
            self.model_related_field: object
        }

    def get(self, request, id):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_403_FORBIDDEN
            )
        object = get_object_or_404(self.model, id=id)
        if user == object:
            return Response(
                {"detail": "You can't subscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        _, created = self.connecting_model.objects.get_or_create(
            **self.get_kwargs(user, object)
        )
        if created:
            serializer = self.serializer_class(object)
            serializer.context['request'] = request
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "The relationship already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_403_FORBIDDEN
            )
        connecting_object = get_object_or_404(
            self.connecting_model,
            **self.get_kwargs(user, id)
        )
        deleted = connecting_object.delete()
        if deleted[0] == 1:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Something went wrong"},
            status=status.HTTP_400_BAD_REQUEST
        )


class CreateDeleteFavoriteView(CreateDeleteRelationView):
    model = Recipes
    connecting_model = Favorite
    serializer_class = PartialRecipesSerializer
    user_related_field = 'lover'
    model_related_field = 'recipe'


class CreateDeleteInCartView(CreateDeleteRelationView):
    model = Recipes
    connecting_model = ShopingCart
    serializer_class = PartialRecipesSerializer
    user_related_field = 'buyer'
    model_related_field = 'recipe'


class CreateDeleteSubscriptionView(CreateDeleteRelationView):
    model = User
    connecting_model = Subscription
    serializer_class = SubscriptionsSerializer
    user_related_field = 'subscriber'
    model_related_field = 'subscribed'


def download_shoping_cart(request):
    user = request.user
    file_path = path.join(
        settings.MEDIA_ROOT, 'shoping_lists', f'{user.username}.txt'
    )
    with open(file_path, 'w') as shoping_list:
        purchases = Recipes.objects.filter(
            buyer__buyer=user
        ).select_related('ingredientrecipe', 'ingredients', 'buyer').annotate(
            ingredient=F('ingredients__name'),
            units=F('ingredients__measurement_unit')
        ).values('ingredient', 'units').annotate(
            amount=Sum('ingredientrecipe__amount')
        ).order_by()
        shoping_list.write('\n\n\n')
        for purchase in purchases:
            line = ' '.join((
                ' ' * 5,
                purchase['ingredient'],
                ' ' * (60 - len(purchase['ingredient'])),
                str(purchase['amount']),
                purchase['units']
            )) + '\n'
            shoping_list.write(line)
        shoping_list.close()
    with open(file_path, 'r') as shoping_list:
        response = HttpResponse(
            shoping_list.read(), content_type="text/plain,charset=utf8"
        )
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        return response

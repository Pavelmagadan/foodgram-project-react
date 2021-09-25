from os import path

from django.db.models import F, Sum

from foodgram import settings
from recipes.models import Recipes


def get_shopping_list(user):
    file_path = path.join(
        settings.MEDIA_ROOT, 'shoping_lists', f'{user.username}.txt'
    )
    purchases = Recipes.objects.filter(
        buyer__buyer=user
    ).select_related('ingredientrecipe', 'ingredients', 'buyer').annotate(
        ingredient=F('ingredients__name'),
        units=F('ingredients__measurement_unit')
    ).values('ingredient', 'units').annotate(
        amount=Sum('ingredientrecipe__amount')
    ).order_by()
    if not purchases.exists():
        return None
    with open(file_path, 'w') as shoping_list:
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
        return file_path

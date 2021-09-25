from rest_framework.pagination import PageNumberPagination

from foodgram import settings


class FootgramPagination(PageNumberPagination):
    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = 1000

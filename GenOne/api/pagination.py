from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 7                     # default page size
    page_size_query_param = 'page_size'  # allow client to override
    max_page_size = 100                # max allowed page size

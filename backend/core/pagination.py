"""
Custom pagination classes for RoadAid Network.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with customizable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallResultsSetPagination(PageNumberPagination):
    """
    Smaller pagination for mobile or lightweight responses.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class LargeResultsSetPagination(PageNumberPagination):
    """
    Larger pagination for admin or bulk operations.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

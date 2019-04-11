# https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            # add my custom properties
            'res_code': 1,
            'res_msg': 'success',
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

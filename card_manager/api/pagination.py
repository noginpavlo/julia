from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    # add docstring
    page_size = 10

    def get_paginated_response(self, data):  # type hinting
        return Response(
            {
                "count": self.page.paginator.count,
                "current": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

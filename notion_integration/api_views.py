"""
Notion API endpoints.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes

from .services import NotionService


class NotionSearchAPIView(APIView):
    """
    Search Notion pages and databases.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Search Notion",
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search query",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Results to return (1-100, default 10)",
            ),
            OpenApiParameter(
                name="start_cursor",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Cursor for pagination",
            ),
            OpenApiParameter(
                name="filter",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Limit results to 'page' or 'database'",
            ),
        ],
        responses={200: dict, 400: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response({"error": "Missing required parameter: q"}, status=status.HTTP_400_BAD_REQUEST)

        page_size = int(request.query_params.get("page_size", 10))
        start_cursor = request.query_params.get("start_cursor")
        filter_type = request.query_params.get("filter")

        try:
            notion = NotionService()
            results = notion.search(query, page_size=page_size, start_cursor=start_cursor, filter_type=filter_type)
            return Response(results, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotionPageDetailAPIView(APIView):
    """
    Retrieve Notion page metadata.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Notion page",
        responses={200: dict, 404: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request, page_id: str):
        try:
            notion = NotionService()
            page = notion.retrieve_page(page_id)
            return Response(page, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotionPageContentAPIView(APIView):
    """
    Retrieve the blocks (content) of a page.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Notion page content",
        parameters=[
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Blocks to return (1-100, default 50)",
            ),
            OpenApiParameter(
                name="start_cursor",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Cursor for pagination",
            ),
        ],
        responses={200: dict, 404: dict, 500: dict},
        tags=["Notion"],
    )
    def get(self, request, page_id: str):
        page_size = int(request.query_params.get("page_size", 50))
        start_cursor = request.query_params.get("start_cursor")

        try:
            notion = NotionService()
            blocks = notion.list_block_children(page_id, page_size=page_size, start_cursor=start_cursor)
            return Response(blocks, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

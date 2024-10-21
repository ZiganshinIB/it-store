from rest_framework import viewsets

from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes

from ..serializers import (
    ListApprovalRouteSerializer,
    DetailApprovalRouteSerializer,
    UpdateApprovalRouteSerializer
)
from mysite.serializers import DummyDetailAndStatusSerializer, DummyDetailSerializer

from ..models import ApprovalRoute



@extend_schema_view(
    list=extend_schema(
            summary="Получить список Маршрутов согласования",
            description="Используя эту комманду вы можете получить список Маршрутов согласования",
            responses={
                200: ListApprovalRouteSerializer(many=True),
                403: DummyDetailAndStatusSerializer
            },
        ),
    update = extend_schema(
        summary="Обновление Маршрута согласования",
        description="Используя эту комманду вы можете обновить Маршрут согласования",
        request=UpdateApprovalRouteSerializer,

    ),
    retrieve=extend_schema(
        summary="Показывает конкретный Маршрут согласования",
        description="Используя эту комманду вы можете показать конкретный Маршрут согласования",
        responses={
            200: DetailApprovalRouteSerializer(many=True),
            403: DummyDetailAndStatusSerializer
        },
    ),
    partial_update=extend_schema(
        summary="Частичное обновление Маршрута согласования",
        description="Используя эту комманду вы можете частично обновить Маршрут согласования",
        request=UpdateApprovalRouteSerializer,
    ),
    create=extend_schema(
            summary="Создание нового Маршрута согласования",
            description="Создается маршрут согласования с шагами.",
            responses={
                201: DetailApprovalRouteSerializer(many=True),
                403: DummyDetailAndStatusSerializer,
                400: DummyDetailSerializer
            },
            request=DetailApprovalRouteSerializer(many=True),

        ),
)
class ApprovalRouteViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           GenericViewSet):
    queryset = ApprovalRoute.objects.all()
    serializer_class = ListApprovalRouteSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer_class(self):
        """
        Возвращает сериализатор для конкретного действия
        :return:
        """
        if self.action == 'create':
            return DetailApprovalRouteSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return UpdateApprovalRouteSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
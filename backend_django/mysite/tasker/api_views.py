from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, views, generics, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from person.serializers import DummyDetailSerializer, DummyDetailAndStatusSerializer

from .models import ApprovalRoute, ApproveStep
from .models import RequestTemplate, RequestTaskRelation, TaskTemplate
from .models import Request, Task, Approve, Comment

from .serializers import (
    ListApprovalRouteSerializer,
    DetailApprovalRouteSerializer,
    UpdateApprovalRouteSerializer,
    TaskTemplateSerializer,
    RequestTaskRelationSerializer,
    ListRequestTemplateSerializer,
    DetailRequestTemplateSerializer,
    UpdateRequestTemplateSerializer,
    TaskSerializer,
    ApproveSerializer,
    CommentSerializer,
    CreateRequestSerializer,
    ListRequestSerializer,
    DetailRequestSerializer,
    AppointRequestSerializer
)

from .permissions import ListRequestPermission, DetailRequestPermission, CanselRequestPermission, \
    AppointRequestPermission


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


@extend_schema_view(
    list=extend_schema(
        summary="Получить список шаблонных заявок",
    ),
    create=extend_schema(
        summary="Создание шаблона заявки",
    ),
    retrieve=extend_schema(
        summary="Получить детальную информацию о шаблонной заявке",
        description="Используя эту комманду вы можете получить детальную информацию о шаблонной заявке",
        request=DetailRequestTemplateSerializer,
        responses={
            200: DetailRequestTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        },
    ),
)
class RequestTemplateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = RequestTemplate.objects.all()
    serializer_class = ListRequestTemplateSerializer
    permission_classes = [DjangoModelPermissions]

    def get_permissions(self):
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailRequestTemplateSerializer
        return super().get_serializer_class()


@extend_schema_view(
    list=extend_schema(
        summary="Получить список шаблонных задач",
    ),
    create=extend_schema(
        summary="Создание шаблона задачи",
    ),
    partial_update=extend_schema(
        summary="Пока в работе",
    ),
    update=extend_schema(
        summary="Пока в работе",
    ),
    destroy=extend_schema(
        summary="Пока в работе",
    ),
    retrieve=extend_schema(
        summary="Пока в работе",
    ),
)
class TaskTemplateViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    permission_classes = [DjangoModelPermissions]


# TODO: Переделать
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [DjangoModelPermissions]

class CreateRequestView(generics.CreateAPIView):
    serializer_class = CreateRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ListRequestView(generics.ListAPIView):
    serializer_class = ListRequestSerializer
    permission_classes = [ListRequestPermission]
    queryset = Request.objects.all()


    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_perm('tasker.view_request'):
            return self.queryset
        else:
            response = self.queryset((Q(group__in=user.groups.all()) | Q(author=user) | Q(executor=user)).distinct())
            return response


class DetailRequestView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = ListRequestSerializer
    permission_classes = [DetailRequestPermission]


@extend_schema_view(
    get=extend_schema(
        summary="Отмена заявки",
        description="Используя эту комманду автор заявки можете отменить заявку",
        responses={
            200: ListRequestSerializer,
            400: DummyDetailAndStatusSerializer
        },
    )
)
class CanselRequestView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = ListRequestSerializer
    permission_classes = [DetailRequestPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in ['aprv', 'new', 'prg']:
            instance.status = 'cans'
            instance.save()
        elif instance.status == 'chk':
            instance.status = 'end'
            instance.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema_view(
    put=extend_schema(
        summary="Назначить заявке исполнителя",
        description="Используя эту можно назначить заявке исполнителя",
        responses={
            200: AppointRequestSerializer,
            403: DummyDetailAndStatusSerializer
        },
    ),
    patch=extend_schema(
        summary="Назначить заявке исполнителя",
        description="Используя эту можно назначить заявке исполнителя",
        responses={
            200: AppointRequestSerializer,
            403: DummyDetailAndStatusSerializer
        },
    ),
)
class AppointRequestView(generics.UpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = AppointRequestSerializer
    permission_classes = [AppointRequestPermission]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


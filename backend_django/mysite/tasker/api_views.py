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

from .serializers import ApprovalRouteSerializer, ApproveStepSerializer
from .serializers import RequestTemplateSerializer, RequestTaskRelationSerializer, TaskTemplateSerializer
from .serializers import TaskSerializer
from .serializers import CreateRequestSerializer, ListRequestSerializer, AppointRequestSerializer

from .permissions import ListRequestPermission, DetailRequestPermission, CanselRequestPermission, \
    AppointRequestPermission


@extend_schema_view(
    list=extend_schema(
            summary="Получить список Маршрутов согласования",
            description="Используя эту комманду вы можете получить список Маршрутов согласования",
            responses={
                200: ApprovalRouteSerializer(many=True),
                403: DummyDetailAndStatusSerializer
            },
        ),
    update=extend_schema(
        summary="Пока в работе",

    ),
    partial_update=extend_schema(
        summary="Пока в работе",
    ),
    create=extend_schema(
            summary="Создание нового Маршрута согласования",
            description="Создается маршрут согласования с шагами.",
            responses={
                201: ApprovalRouteSerializer(many=True),
                403: DummyDetailAndStatusSerializer,
                400: DummyDetailSerializer
            },
            request=ApprovalRouteSerializer(many=True),

        ),
)
class ApprovalRouteViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRoute.objects.all()
    serializer_class = ApprovalRouteSerializer
    permission_classes = [DjangoModelPermissions]

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
class RequestTemplateViewSet(viewsets.ModelViewSet):
    queryset = RequestTemplate.objects.all()
    serializer_class = RequestTemplateSerializer
    permission_classes = [DjangoModelPermissions]


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


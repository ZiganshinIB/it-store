from http.client import responses
from trace import Trace

from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, views, generics, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from mysite.permissions import AdvanceDjangoModelPermissions
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
    AppointRequestSerializer, CreateRequestTemplateSerializer, AppendTaskTemplateSerializer
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
    destroy=extend_schema(
        summary="Удаление Маршрута согласования",
        description="Используя эту комманду вы можете удалить Маршрут согласования",
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
    permission_classes = [AdvanceDjangoModelPermissions]

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список шаблонных задач",
        description="Используя эту комманду вы можете получить список шаблонных задач",
        responses={
            200: TaskTemplateSerializer(many=True),
            403: DummyDetailAndStatusSerializer
        }
    ),
    create=extend_schema(
        summary="Создание шаблона задачи",
        description="Используя эту комманду вы можете создать шаблон задачи",
        request=TaskTemplateSerializer,
        responses={
            201: TaskTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
    ),
    partial_update=extend_schema(
        summary="Обновить шаблон задачи",
        description="Используя эту комманду вы можете частично обновить шаблон задачи",
        request=TaskTemplateSerializer,
        responses={
            200: TaskTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
    ),
    update=extend_schema(
        summary="Пока в работе",
        description="Используя эту комманду вы можете пока в работе",
        request=TaskTemplateSerializer,
        responses={
            200: TaskTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
    ),
    destroy=extend_schema(
        summary="Удалить шаблон задачи",
        description="Используя эту комманду вы можете удалить шаблон задачи",
    ),
    retrieve=extend_schema(
        summary="Получить детальную информацию о шаблоне задачи",
        description="Используя эту комманду вы можете получить детальную информацию о шаблоне задачи",
        responses={
            200: TaskTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
    ),
)
class TaskTemplateViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    permission_classes = [AdvanceDjangoModelPermissions]


@extend_schema_view(
    list=extend_schema(
        summary="Получить список шаблонных заявок",
        description="Используя эту комманду вы можете получить список шаблонных заявок",
        responses={
            200: ListRequestTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
    ),
    create=extend_schema(
        summary="Создание шаблона заявки",
        description="Используя эту комманду вы можете создать шаблон заявки",
        request=CreateRequestTemplateSerializer,
        responses={
            201: DetailRequestTemplateSerializer,
            403: DummyDetailAndStatusSerializer
        }
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
    clean_tasks=extend_schema(
        summary="Очистить шаблонные задачи",
        description="Это комманда очистит все связанные шаблонные задачи из шаблона заявок",

)

)
class RequestTemplateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    queryset = RequestTemplate.objects.all()
    serializer_class = ListRequestTemplateSerializer
    permission_classes = [AdvanceDjangoModelPermissions]

    def get_permissions(self):
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailRequestTemplateSerializer
        if self.action == 'create':
            return CreateRequestTemplateSerializer
        if self.action == 'partial_update' or self.action == 'update':
            return UpdateRequestTemplateSerializer
        if self.action == 'add_task':
            return AppendTaskTemplateSerializer
        return super().get_serializer_class()

    @action(methods=['delete'], detail=True)
    def clean_tasks(self, request, pk=None):
        """
        Удаляет все связи с Шаблонами задач
        Результат: self.tasks == []
        """
        instance = self.get_object()
        instance.tasks.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def add_task(self, request, pk=None):
        """
        Добавляет шаблон задачи в список шаблонов задач
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        response = DetailRequestTemplateSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = DetailRequestTemplateSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)





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


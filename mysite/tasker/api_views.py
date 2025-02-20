from django.db.models import Q

from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, views, generics, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, AllowAny

from person.serializers import DummyDetailSerializer, DummyDetailAndStatusSerializer

from . import permissions
from .models import (
    ApprovalRoute, ApproveStep,
    RequestTemplate, RequestTaskRelation, TaskTemplate,
    Request, Task, Approve, Comment
)
from .permissions.Base import IsAuthor, IsCheck

from .serializers import (
    ListApprovalRouteSerializer, DetailApprovalRouteSerializer, UpdateApprovalRouteSerializer,
    TaskTemplateSerializer,
    ListRequestTemplateSerializer, DetailRequestTemplateSerializer, UpdateRequestTemplateSerializer,
    TaskSerializer, DetailTaskSerializer, CreateTaskSerializer,
    CreateRequestSerializer,
    CreateRequestTemplateSerializer,
    AppendTaskTemplateSerializer, CommentSerializer, AuthorUpdateTaskSerializer, UpdateTaskSerializer,
    ListRequestSerializer, DetailRequestSerializer,
)


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
    permission_classes = [permissions.Base.AdvanceDjangoModelPermissions]

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
    permission_classes = [permissions.Base.AdvanceDjangoModelPermissions]


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
    permission_classes = [permissions.Base.AdvanceDjangoModelPermissions]

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = DetailRequestTemplateSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

@extend_schema_view(
    list=extend_schema(
        summary="Получить список задач",
        description="Используя эту комманду вы можете получить список задач",
        responses={
            200: TaskSerializer,
        },
        tags=["Управление задачами"]
    ),
    retrieve=extend_schema(
        summary="Получить детальную информацию о задаче",
        description="Используя эту комманду вы можете получить детальную информацию о задаче",
        responses={
            200: TaskSerializer
        },
        tags=["Управление задачами"]
    ),
    create=extend_schema(
        summary="Создание задачи",
        description="Используя эту комманду вы можете создать задачу",
        request=CreateTaskSerializer,
        responses={
            201: DetailTaskSerializer
        },
        tags=["Управление задачами"]
    ),
    update=extend_schema(
        summary="Изменить задачу",
        description="Используя эту комманду вы можете изменить задачу",
        request=UpdateTaskSerializer,
        responses={
            200: DetailTaskSerializer
        },
        tags=["Управление задачами",]
    ),
    partial_update=extend_schema(
        summary="Изменить задачу",
        description="Используя эту комманду вы можете изменить задачу",
        request=UpdateTaskSerializer,
        responses={
            200: DetailTaskSerializer
        },
        tags=["Управление задачами",]
    ),
    comment=extend_schema(
        summary="Добавить комментарии к задаче",
        description="Используя эту комманду вы можете добавить комментарии к задаче",
        request=CommentSerializer,
        responses={
            201: CommentSerializer,
            403: DummyDetailAndStatusSerializer
        },
        tags=["Управление задачами", "Комментирование"]
    ),
    change=extend_schema(
        summary="Изменить задачу",
        description="Используя эту комманду вы можете изменить задачу",
        request=AuthorUpdateTaskSerializer,
        responses={
            200: DetailTaskSerializer
        },
        tags=["Управление задачами", "Изменение"]
    ),
    cansel=extend_schema(
        summary="Отменить задачу",
        description="Используя эту комманду вы можете отменить задачу",
        responses={
            200: DetailTaskSerializer
        },
        tags=["Управление задачами", "Отмена"]
    )
)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [DjangoModelPermissions]

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'cansel':
            permission_classes+= [permissions.Base.IsAuthor]
            return [permission() for permission in permission_classes]
        if self.action == 'comment':
            return [permission() for permission in permission_classes]
        if self.action == 'change':
            permission_classes += [permissions.Base.IsAuthor, permissions.Task.IsNew]
            return [permission() for permission in permission_classes]
        if self.action in ['update', 'partial_update']:
            permission_classes += [(permissions.Base.IsGroup|permissions.Base.IsExecutor), permissions.Task.CanChange]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailTaskSerializer
        if self.action == 'cansel':
            return DetailTaskSerializer
        if self.action == 'create':
            return CreateTaskSerializer
        if self.action == "comment":
            return CommentSerializer
        if self.action == "change":
            return AuthorUpdateTaskSerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateTaskSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_superuser or self.request.user.has_perm('tasker.view_task'):
            return self.queryset
        queryset = self.queryset.filter(
            (
                    Q(author=user) | Q(executor=user) | Q(group__in=user.groups.all()))
        ).distinct()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = DetailTaskSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response = DetailTaskSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_200_OK)

    @action(["get"], detail=True)
    def cansel(self, request, pk):
        """
        Комманда для отмены задачи
        """
        task = self.get_object()
        task.status = 'cans'
        task.closed_at = timezone.now()
        task.cansel_date = timezone.now()
        comment = Comment(content_object=task, title="Задача отменена", author=self.request.user, content="Задача отменена", )
        comment.save()
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(["post"], detail=True)
    def comment(self, request, pk):
        """
        Комманда для добавления комментария к задаче
        """
        task = self.get_object()
        comment = self.get_serializer(data=request.data)
        comment.is_valid(raise_exception=True)
        comment.save(author=self.request.user, content_object=task)
        return Response(comment.data, status=status.HTTP_201_CREATED)

    @action(["put", "patch"], detail=True)
    def change(self, request, pk):
        """
        Комманда для изменения задачи Автором.
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = DetailTaskSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="Просмотр всех запросов",
        description="Просмотр всех запросов",
        tags=["Запросы"],
        responses={
            200: ListRequestSerializer,
        },
    ),
    retrieve=extend_schema(
        summary="Просмотр одного запроса",
        description="Просмотр одного запроса",
        tags=["Запросы"],
        responses={
            200: DetailRequestSerializer,
        }
    ),
    create=extend_schema(
        summary="Создание запроса",
        description="Создание запроса",
        tags=["Запросы"],
        request=CreateRequestSerializer,
        responses={
            201: DetailRequestSerializer,
        }

    ),
    cansel=extend_schema(
        summary="Отмена заявки",
        description="Только автор заявки может отменить заявку."
                    "При отмене заявки статус заявки меняется на 'cans'"
                    "Также отменяются все активные согласовании и задачи."
                    "Возвращает обновленную заявку",
        tags=["Запросы"],
        responses={
            200: DetailRequestSerializer
        },
        methods=['get'],
    ),
    end=extend_schema(
        summary="Завершение заявки",
        description="Только автор заявки может завершить заявку."
                    "При завершении заявки статус заявки меняется на 'end'"
                    "Также отменяются все активные согласовании и задачи."
                    "Возвращает обновленную заявку",
        tags=["Запросы"],
        responses={
            200: DetailRequestSerializer
        },
        methods=['get'],
    ),
)
class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = ListRequestSerializer
    permission_classes = [DjangoModelPermissions]

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'create':
            permission_classes.append(AllowAny)
        elif self.action == 'cansel':
            permission_classes.append(IsAuthor)
        elif self.action == 'end':
            permission_classes.append(IsAuthor)
        else:
            permission_classes.append(DjangoModelPermissions)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'cansel', 'end']:
            return DetailRequestSerializer
        if self.action == 'create':
            return CreateRequestSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_perm('tasker.view_request'):
            return self.queryset
        else:
            user_groups = user.groups.all()
            queryset = self.queryset.prefetch_related(
                'approves',
                'tasks'
            ).filter(
                Q(author=user) |
                Q(executor=user) |
                Q(group__in=user_groups) |
                Q(approves__author=user) |
                Q(approves__coordinating=user) |
                Q(tasks__author=user) |
                Q(tasks__executor=user) |
                Q(tasks__group__in=user_groups)
            ).distinct()
            return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = DetailRequestSerializer(instance=serializer.instance)
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["get"], detail=True)
    def cansel(self, request, pk) :
        """
        При отмене заявки статус заявки меняется на 'cans'.
        Также отменяются все активные согласования и задачи.
        Возвращает обновленную заявку (DetailRequestSerializer)
        :return: Data json DetailRequestSerializer
        """
        my_request = self.get_object()
        my_request.status = 'cans'
        my_request.closed_at = timezone.now()
        my_request.cansel_date = timezone.now()
        tasks = my_request.tasks.filter(status__in=['new', 'prg', 'aprv', 'chk'])
        tasks.update(status='cans', cansel_date=timezone.now(), closed_at=timezone.now())
        approves = my_request.approves.filter(status__in=['new', 'prg', 'aprv', 'chk'])
        approves.update(status='cans', cansel_date=timezone.now(),)
        my_request.save()
        my_request = self.get_object()
        response = self.get_serializer(my_request)
        return Response(response.data, status=status.HTTP_200_OK)

    @action(["get"], detail=True)
    def end(self, request, pk):
        """
        При завершении заявки статус заявки меняется на 'end'.
        Также отменяются все активные согласования и задачи.
        Возвращает обновленную заявку (DetailRequestSerializer)
        :return:
        """
        my_request = self.get_object()
        if my_request.status != 'chk':
            # raise ValidationError("Заявка должна быть в статусе 'chk'")
            return Response("{\"detail\":\"Заявка должна быть в статусе 'chk'\"}", status=status.HTTP_400_BAD_REQUEST)
        my_request.status = 'end'
        my_request.cansel_date = timezone.now()
        my_request.save()
        # get data tasks and approves
        tasks = my_request.tasks.filter(status__in=['new', 'prg', 'aprv', 'chk'])
        tasks.update(status='end', cansel_date=timezone.now(), closed_at=timezone.now())
        approves = my_request.approves.filter(status__in=['new', 'prg', 'aprv', 'chk'])
        approves.update(status='end', cansel_date=timezone.now(),)







# class ListRequestView(generics.ListAPIView):
#     serializer_class = ListRequestSerializer
#     permission_classes = [ListRequestPermission]
#     queryset = Request.objects.all()
#
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser or user.has_perm('tasker.view_request'):
#             return self.queryset
#         else:
#             response = self.queryset((Q(group__in=user.groups.all()) | Q(author=user) | Q(executor=user)).distinct())
#             return response
#
#
# class DetailRequestView(generics.RetrieveAPIView):
#     queryset = Request.objects.all()
#     serializer_class = ListRequestSerializer
#     permission_classes = [DetailRequestPermission]
#
#
# @extend_schema_view(
#     get=extend_schema(
#         summary="Отмена заявки",
#         description="Используя эту комманду автор заявки можете отменить заявку",
#         responses={
#             200: ListRequestSerializer,
#             400: DummyDetailAndStatusSerializer
#         },
#     )
# )
# class CanselRequestView(generics.RetrieveAPIView):
#     queryset = Request.objects.all()
#     serializer_class = ListRequestSerializer
#     permission_classes = [DetailRequestPermission]
#
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         if instance.status in ['aprv', 'new', 'prg']:
#             instance.status = 'cans'
#             instance.save()
#         elif instance.status == 'chk':
#             instance.status = 'end'
#             instance.save()
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#
#
# @extend_schema_view(
#     put=extend_schema(
#         summary="Назначить заявке исполнителя",
#         description="Используя эту можно назначить заявке исполнителя",
#         responses={
#             200: AppointRequestSerializer,
#             403: DummyDetailAndStatusSerializer
#         },
#     ),
#     patch=extend_schema(
#         summary="Назначить заявке исполнителя",
#         description="Используя эту можно назначить заявке исполнителя",
#         responses={
#             200: AppointRequestSerializer,
#             403: DummyDetailAndStatusSerializer
#         },
#     ),
# )
# class AppointRequestView(generics.UpdateAPIView):
#     queryset = Request.objects.all()
#     serializer_class = AppointRequestSerializer
#     permission_classes = [AppointRequestPermission]
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             instance._prefetched_objects_cache = {}
#
#         return Response(serializer.data)


from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
# contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

UserModel = get_user_model()

class ApprovalRoute(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    author = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Маршрут согласования'
        verbose_name_plural = 'Маршруты согласования'


class ApproveStep(models.Model):
    APPROVAL_TYPE = (
        ('specific', 'Конкретный'),
        ('manager', 'Начальник'),
        ('group', 'Группа'),
    )
    title = models.CharField(max_length=100, verbose_name='Тема согласования')
    route = models.ForeignKey(ApprovalRoute, on_delete=models.CASCADE, verbose_name='Маршрут согласования', related_name='steps')
    order_number = models.IntegerField(verbose_name='Порядковый номер')
    approval_type = models.CharField(max_length=10, choices=APPROVAL_TYPE, verbose_name='Тип согласования')
    specific_approver = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Согласователь')
    group_approver = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа')
    dedlin = models.DurationField(verbose_name='Срок выполнения задачи', blank=True, null=True, default=timezone.timedelta(days=1, hours=0, minutes=0))

    def __str__(self):
        return self.title

    def clean(self):
        if self.approval_type == 'group' and not self.group_approver:
            raise ValidationError("Укажите группу")
        if self.approval_type == 'specific' and not self.specific_approver:
            raise ValidationError("Укажите согласователя")
        return self

    class Meta:
        verbose_name = 'Шаг согласования'
        verbose_name_plural = 'Шаги согласования'
        ordering = ['order_number']


class TaskTemplate(models.Model):
    """
    Шаблон задачи
    """
    COMPLEXITY = (
        ('low', 'Низкая'),
        ('med', 'Средняя'),
        ('hig', 'Высокая'),
    )
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа')
    dedline = models.DurationField(verbose_name='Срок выполнения задачи', blank=True, null=True, default=timezone.timedelta(days=1, hours=0, minutes=0))
    complexity = models.CharField(max_length=3, choices=COMPLEXITY, verbose_name='Сложность', blank=True, default='med')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Шаблон задачи'
        verbose_name_plural = 'Шаблоны задач'


# Шаблон Заявки
class RequestTemplate(models.Model):
    COMPLEXITY = (
        ('low', 'Низкая'),
        ('med', 'Средняя'),
        ('hig', 'Высокая'),
    )
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    image = models.ImageField(upload_to='media/request/', verbose_name='Изображение', blank=True, null=True)
    approval_route = models.ForeignKey(ApprovalRoute, on_delete=models.SET_NULL, verbose_name='Маршрут согласования',
                                       blank=True, null=True, default=None)
    dedline = models.DurationField(verbose_name='Срок выполнения задачи', blank=True, null=True, default=timezone.timedelta(days=3, hours=0, minutes=0))
    complexity = models.CharField(max_length=3, choices=COMPLEXITY, verbose_name='Сложность')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, verbose_name='Группа', blank=True, null=True, default=None)
    tasks = models.ManyToManyField(TaskTemplate, verbose_name='Задачи', through='RequestTaskRelation', blank=True, default=None,)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Шаблон заявки'
        verbose_name_plural = 'Шаблоны заявок'


class RequestTaskRelation(models.Model):
    request_template = models.ForeignKey(RequestTemplate, on_delete=models.CASCADE)
    task_template = models.ForeignKey(TaskTemplate, on_delete=models.CASCADE, verbose_name='Шаблон задачи')
    additional_info = models.CharField(max_length=100, verbose_name='Дополнительная информация', blank=True, null=True)

    class Meta:
        unique_together = ('request_template', 'task_template')
        verbose_name = 'Задача шаблона заявки'
        verbose_name_plural = 'Задачи шаблона заявки'

class Request(models.Model):
    """
    Заявка
    """
    STATUS = (
        ('new', 'Новый'),
        ('prg', 'В работе'),
        ('aprv', 'Согласование'),
        ('cans', 'Отменен'),
        ('clos', 'Отклонен'),
        ('chk', 'Проверяет пользователь'),
        ('end', 'Завершен')
    )
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')
    dedlin_date = models.DateTimeField(verbose_name='Крайний срок выполнения')
    cansel_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершение")
    author = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Автор', related_name='requests')
    executor = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                 verbose_name='Исполнитель')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, default=None,)
    status = models.CharField(max_length=10, choices=STATUS, default='new',
                              verbose_name='Статус')
    request_template = models.ForeignKey(RequestTemplate, on_delete=models.SET_NULL, null=True,
                                         verbose_name='Шаблон заявки')
    # Для связи между заявками и комментариями. Далее вы сможете фильтровать заявки по комментариям
    comments = GenericRelation('Comment', related_query_name='request')


    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class Task(models.Model):
    STATUS = (
        ('new','Новый'),
        ('prg' ,'В работе'),
        ('aprv','Согласование'),
        ('cans','Отменен'),
        ('clos','Откланен'),
        ('chk', 'Проверяет пользователь'),
        ('end','Завершен')
    )
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')
    dedlin_date = models.DateTimeField(verbose_name='Крайний срок выполнения', blank=True, null=True,
                                       default=timezone.timedelta(days=3, hours=0, minutes=0))
    cansel_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершение")
    author = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Автор', related_name='task_author')
    executor = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Исполнитель')
    status = models.CharField(max_length=10, choices=STATUS, verbose_name='Статус', default='new')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Группа')
    task_template = models.ForeignKey(TaskTemplate, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Тип')
    on_request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Заявка', related_name='tasks')

    comments = GenericRelation('Comment', related_query_name='task')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True,   verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def cansel(self):
        """
        Отмена задачи
        """
        self.status = 'cans'
        self.cansel_date = timezone.now()
        self.save()


class Approve(models.Model):
    """
    Согласование задачи
    """
    STATUS = (
        ('new', 'Новый'),
        ('prg', 'В работе'),
        ('aprv', 'Согласованный'),
        ('cans', 'Отменен'),
        ('clos', 'Откланен'),
    )
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    order_number = models.IntegerField(verbose_name='Порядковый номер', blank=True, null=True, default=None)
    author = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Автор', related_name='author_approve')
    on_request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, verbose_name='Заявка', related_name='approves')
    coordinating = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Согласователь', related_name='coordinating_approve')
    status = models.CharField(max_length=10, choices=STATUS, verbose_name='Статус', default='new')
    cansel_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершение")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Согласование'
        verbose_name_plural = 'Согласования'


class Comment(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок', blank=True, null=True)
    author = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        constraints = [
            models.UniqueConstraint(fields=['author', 'content_type', 'object_id'], name='unique_comment')
        ]

#     # Example filter
#     # Comment.objects.filter(content_type=ContentType.objects.get_for_model(Task))

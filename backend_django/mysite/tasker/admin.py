from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import ApprovalRoute, ApproveStep
from .models import RequestTemplate, TaskTemplate, RequestTaskRelation
from .models import Request, Task, Approve, Comment


class ApproveStepInline(admin.TabularInline):
    model = ApproveStep
    extra = 1  # Количество пустых форм для добавления новых шагов

@admin.register(ApprovalRoute)
class ApprovalRouteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    inlines = [ApproveStepInline]
    search_fields = ('title', 'description')
    exclude = ('created_at', 'updated_at', 'author')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ApproveStep)
class ApproveStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'approval_type', 'order_number')
    search_fields = ('title',)

    def has_add_permission(self, request):
        return False  # Запретить добавление

    def has_change_permission(self, request, obj=None):
        return False  # Запретить изменение

    def has_delete_permission(self, request, obj=None):
        return False  # Запретить удаление

class RequestTaskRelationInline(admin.TabularInline):
    model = RequestTaskRelation
    extra = 1  # Количество пустых форм для добавления новых связей


@admin.register(RequestTemplate)
class RequestTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'complexity', 'dedline')
    inlines = [RequestTaskRelationInline]  # Добавляем inline для промежуточной модели


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'dedline')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    search_fields = ('title', 'description')
    exclude = ('created_at', 'updated_at', 'author')

class TaskInline(admin.TabularInline):
    model = Task
    exclude = ('description', 'cansel_date', 'closed_at', 'author', 'task_template')
    extra = 1  # Количество пустых форм для добавления новых задач
    readonly_fields = ('status',)
    show_change_link = True

@admin.register(Approve)
class ApproveAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    search_fields = ('title', 'description')


class ApproveInline(admin.TabularInline):
    model = Approve
    extra = 1  # Количество пустых форм для добавления новых согласований
    exclude = ('description', 'author', 'cansel_date')
    readonly_fields = ('status',)
    show_change_link = True


class CommentInline(GenericTabularInline):
    model = Comment
    extra = 1  # Количество пустых форм для добавления новых комментариев
    readonly_fields = ('author',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    inlines = [TaskInline, ApproveInline, CommentInline]
    list_display = ('title', 'status', 'created_at')
    search_fields = ('title', 'description')
    exclude = ('created_at', 'updated_at', 'author', 'cansel_date', 'closed_at')





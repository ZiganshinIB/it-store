# Generated by Django 5.1.1 on 2024-10-10 10:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tasker', '0005_requesttemplate_group'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesttemplate',
            name='tasks',
            field=models.ManyToManyField(blank=True, default=None, null=True, through='tasker.RequestTaskRelation', to='tasker.tasktemplate', verbose_name='Задачи'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('dedlin_date', models.DateTimeField(verbose_name='Крайний срок выполнения')),
                ('cansel_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершение')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('prg', 'В работе'), ('aprv', 'Согласование'), ('cans', 'Отменен'), ('clos', 'Откланен'), ('chk', 'Проверяет пользователь'), ('end', 'Завершен')], default='new', max_length=10, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('executor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('request_template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasker.requesttemplate', verbose_name='Шаблон заявки')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
        migrations.CreateModel(
            name='Approve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('aprv', 'Согласованный'), ('cans', 'Отменен'), ('clos', 'Откланен')], max_length=10, verbose_name='Статус')),
                ('cansel_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_approve', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('coordinating', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Согласователь')),
                ('on_request', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasker.request', verbose_name='Заявка')),
            ],
            options={
                'verbose_name': 'Согласование',
                'verbose_name_plural': 'Согласования',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('dedlin_date', models.DateTimeField(verbose_name='Крайний срок выполнения')),
                ('cansel_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершение')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('prg', 'В работе'), ('aprv', 'Согласование'), ('cans', 'Отменен'), ('clos', 'Откланен'), ('chk', 'Проверяет пользователь'), ('end', 'Завершен')], max_length=10, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_author', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('executor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('on_request', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasker.request', verbose_name='Заявка')),
                ('task_template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasker.tasktemplate', verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
            },
        ),
    ]

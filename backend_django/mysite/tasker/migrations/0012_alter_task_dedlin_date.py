# Generated by Django 5.1.1 on 2024-10-26 06:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasker', '0011_tasktemplate_group_alter_task_on_request_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='dedlin_date',
            field=models.DateTimeField(blank=True, default=datetime.timedelta(days=3), null=True, verbose_name='Крайний срок выполнения'),
        ),
    ]
# Generated by Django 5.1.1 on 2024-10-27 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasker', '0014_rename_dedline_tasktemplate_dedlin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesttemplate',
            name='tasks',
            field=models.ManyToManyField(blank=True, through='tasker.RequestTaskRelation', to='tasker.tasktemplate', verbose_name='Задачи'),
        ),
    ]

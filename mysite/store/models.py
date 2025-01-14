from django.db import models

# ИТС - оборудование, программамное обеспечение

# Оборудование - модель оборудования
class Equipment(models.Model):
    code = models.CharField(max_length=100, verbose_name='Код оборудования')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='Изображение')

    crated_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'


# Программное обеспечение - модель программного обеспечения
class Software(models.Model):
    code = models.CharField(max_length=100, verbose_name='Код программного обеспечения')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='Изображение')


    def __str__(self):
        return self.name

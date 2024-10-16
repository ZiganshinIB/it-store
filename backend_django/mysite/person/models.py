from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from .managers import PersonManager




class Company(models.Model):
    short_name = models.CharField("Кароткое название", max_length=16)
    name = models.CharField("Польное название", max_length=255, unique=True)
    inn = models.CharField("ИНН", max_length=12, )
    city = models.CharField("Город", max_length=100, null=True, blank=True)
    address = models.CharField("Адрес", max_length=255, null=True, blank=True)
    website = models.URLField("Веб-сайт", max_length=255, null=True, blank=True)
    email = models.EmailField("Почта", max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField("телефоный номер", blank=True)
    employees_count = models.PositiveIntegerField("Количество сотрудников", blank=True, default=0)
    industry = models.CharField("Отрасль", max_length=100, null=True, blank=True)
    description = models.TextField("Описание компании", null=True, blank=True)


    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        # permissions = (
        #     ("view_company", "Может просматривать компании"),
        #     ("add_company", "Может добавлять компании"),
        #     ("change_company", "Может изменять компании"),
        #     ("delete_company", "Может удалять компании"),
        # )
        permissions = (
            ("create_employee", "Может создавать сотрудников"),
        )

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания', related_name='departments')
    deportment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Отдел', related_name='subdepartments')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отдел', related_name='positions')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Person(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_("first name"), max_length=150, )
    last_name = models.CharField(_("last name"), max_length=150, )
    surname = models.CharField("Отчество", max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    phone_number = PhoneNumberField("Телефный номер", blank=True)
    birthday = models.DateField("День рождения", null=True, blank=True)
    position = models.ForeignKey(Position, models.SET_NULL, null=True, blank=True, verbose_name="Должность")
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees',
    )

    objects = PersonManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


    def get_full_name(self):
        """
        Возвращает фамилии, имя и отчество с пробелом между ними
        """
        full_name = "%s %s %s" % (self.last_name, self.first_name, self.surname)
        return full_name.strip()


    def get_short_name(self):
        """Возвращает Фамилию и инициалы."""
        if self.surname:
            short_name = f"{self.last_name} {self.first_name[0]}. {self.surname[0]}."
        else:
            short_name = f"{self.last_name} {self.first_name[0]}."
        return short_name

    def has_group(self, group_name):
        """Проверяет, является ли пользователь членом группый."""
        if self.is_superuser:
            return True
        return self.groups.filter(name=group_name).exists()


    def email_user(self, subject, message, from_email=None, **kwargs):
        """Отправляет электронное письмо этому пользователю."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from transliterate import translit
import re


class PersonManager(BaseUserManager):
    use_in_migrations = True
    def _generate_user_name_(self, first_name, last_name):
        username = f"{translit(first_name, 'ru', reversed=True)}.{translit(last_name, 'ru', reversed=True)}".strip('`').lower()
        username = re.sub(r"[`'@]", "", username)
        if self.filter(username=username).exists():
            username = f"{username}{self.count()}"
        return username

    def create_user(self, first_name, last_name, username=None, password=None, **extra_fields):
        if not first_name:
            raise ValueError("Имя пользователя не может быть пустым")
        first_name = self.model.normalize_username(first_name)
        if not last_name:
            raise ValueError("Фамилия пользователя не может быть пустой")
        last_name = self.model.normalize_username(last_name)
        if not username:
            username = self._generate_user_name_(first_name, last_name)

        username = self.model.normalize_username(username)
        if extra_fields.get('email', None) is None:
            email = f'{username}@test.ru'
        else:
            email = extra_fields.get('email')
            extra_fields.pop('email')
        if password is None:
            password = self.model.make_random_password()
        person = self.model(username=username, first_name=first_name, last_name=last_name, email=email, **extra_fields)
        person.set_password(password)
        person.save(using=self._db)
        return person



    def create_superuser(self, username, first_name, last_name, password, **extra_fields):
        print("Start create_superuser")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, first_name, last_name, password, **extra_fields)

    def with_perm(
            self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()

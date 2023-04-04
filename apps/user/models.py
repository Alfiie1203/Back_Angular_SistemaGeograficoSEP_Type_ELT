from apps.user.views.groups import Check_user_in_groups

from cities_light.models import Country, Region, SubRegion
from config import settings

from apps.utils.models import base_model
from django.contrib.auth.models import (AbstractUser, BaseUserManager, Group)
from django.db import models
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.db.models.signals import pre_save, post_save
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


import uuid
import random


class Role(base_model.BaseModel):
    name = models.CharField(max_length=126)
    groups = models.ManyToManyField(
        Group,
        blank = True,
    )
    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser,):
    username = None
    last_name = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    """Use the email as unique username."""
    REQUIRED_FIELDS = ['first_name', 'surname']
    first_name = models.CharField(max_length=128)
    second_name = models.CharField(max_length=128, blank=True)
    surname = models.CharField(max_length=128)
    second_surname = models.CharField(max_length=128, blank=True)
    image_profile = models.ImageField(
        upload_to = 'user-profile/img/',
        null = True,
        blank = True,
    )
    created_date = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(
        Role,
        on_delete = models.PROTECT,
        null = True,
        blank = True,
    )
    #Contact Info
    company = models.ForeignKey(
        'company.Company',
        on_delete = models.PROTECT,
        blank=True,
        null=True,
    )
    indicative = models.CharField(max_length=16)
    phone = models.CharField(max_length=16)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        blank=True,
        null=True
        )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        SubRegion,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    accept_terms_conditions = models.BooleanField(default=False)
    accept_terms_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=True)

    objects = UserManager()

    class Meta:
        ordering = ['pk']
        permissions=[
            ("change_own_user", "Can change own user")]
        

    def password_reset_mail(self, password_reset_slug:str ) -> None:
        url_password_reset_done = f'{settings.URL_PASSWORD_RESET}{password_reset_slug}'

        email_info = {
            'subject': 'Proforest - Restaurar contraseña.',
            'template': 'password_reset',
            'to': [self.email],
            'context': {
                'user': f'{self.first_name} {self.second_name}' if self.first_name else self.email,
                'url_password_reset_done': url_password_reset_done,
                
            },
        }

        self.send_mail(**email_info)

    def verify_email(self):
        email_info = {
            'subject': 'Proforest - Confirmación de cuenta.',
            'template': 'initial_verify_email',
            'to': [self.email],
            'context': {
                'user': f'{self.first_name} {self.second_name}' if self.first_name else self.email,
                'token': self.slug
            },
        }

        self.send_mail(**email_info)

    def send_mail(self, subject: str, to: list, template: str, context: dict) -> None:
        body = render_to_string(
            f'mail/{template}.html',
            context
        )
        email_message = EmailMessage(
            **{
                'subject': subject,
                'from_email': settings.EMAIL_FROM_DIR,
                'to': to,
                'body': body
            }
        )

        email_message.content_subtype = 'html'
        email_message.send()
    
    def get_full_name(self) -> str:
        return ' '.join((self.first_name, self.second_name, self.surname, self.second_surname))

    def get_image_profile_url(self):
        if self.image_profile:
            return self.image_profile.url
        else:
            return ''
    
    def get_country_display(self):
        if self.country:
            
            return self.country.name
        return _('No Register')

    def get_region_display(self):
        if self.region:
            return self.region.name
        return _('No Register')

    def get_city_display(self):
        if self.city:
            return self.city.name
        return _('No Register')

   

@receiver(post_save, sender=User)
def update_company_asociated(sender, **kwargs):
    from apps.company.models.company import Company #avoid circular importation
    instance = kwargs.get('instance')
    if instance.company:
        update_company = instance.company
        update_company.has_responsable = True
        update_company.save()
    try:
        groups = ['SUPERUSUARIO']
        if Check_user_in_groups(instance, groups):
            
            update_company = instance.company
            update_company.has_superuser = True
            update_company.save()
    except:
        pass #No company
    if instance.status == True:
        instance.is_active = True
    else :
        instance.is_active = False
    return

@receiver(pre_save, sender=User)
def update_company_asociated(sender, **kwargs):
    instance = kwargs.get('instance')
   
    if instance.status == True:
        instance.is_active = True
    else :
        instance.is_active = False
    return

class PasswordReset(base_model.BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    recovery_code = models.IntegerField(blank=True,null=True)

    def get_recovery_code_str(self):
        str_recovery_code = ''
        for l in str(self.recovery_code):
            str_recovery_code += f'{l}'

        return str_recovery_code.strip()

@receiver(pre_save, sender=PasswordReset)
def slug_handler(sender, **kwargs):
    instance = kwargs.get('instance')

    if not instance.slug:
        for _ in range(16):
            slug = uuid.uuid4()

            if not sender.objects.filter(slug=slug).exists():
                instance.slug = slug
                return



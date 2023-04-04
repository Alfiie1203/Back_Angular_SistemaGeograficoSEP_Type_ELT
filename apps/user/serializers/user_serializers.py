from apps.user.models import User
from apps.menu.models import MenuPermissions
from apps.cities.serializers import CountriesSerializer, RegionsSerializer, SubRegionsSerializer
from .role_serializer import RoleSerializerDetail
from apps.company.serializers.company_serializer import CompanySerializerDetail

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import check_password
from django.contrib.contenttypes.models import ContentType

from django.core.validators import EmailValidator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from rest_framework.exceptions import ValidationError

from apps.user.models import User
from apps.company.models.company import Company, ActorType
from apps.company.models.company_group import CompanyGroup
from apps.company.models.commodity import Commodity
from apps.questionsbank.models.questionbank import QuestionBank, Category, SubCategory, Topic
from apps.proforestform.models.proforestform import ProforestForm


class UserSerializerDetail(serializers.ModelSerializer):
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)
    role = RoleSerializerDetail(read_only=True)
    company = CompanySerializerDetail(read_only=True)
    permissions_detail = serializers.SerializerMethodField(
        'get_user_permissions_detail')
    permissions = serializers.SerializerMethodField('get_user_permissions')
    groups = serializers.SerializerMethodField('get_subrole_info')

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'second_name', 'surname', 'second_surname',
                  'role', 'groups', 'company', 'indicative', 'phone', 'country', 'region', 'city', 'status',
                  'permissions', 'permissions_detail']

    def get_user_permissions(self, obj):
        return list(obj.get_group_permissions())

    def get_user_permissions_detail(self, obj):
        dict = {}
        if obj.groups.all().count() > 0:
            for perm in obj.groups.all()[0].permissions.all():
                if perm.content_type.model not in dict:
                    dict[perm.content_type.model] = [perm.codename]
                else:
                    dict[perm.content_type.model].append(perm.codename)
            return dict
        else:
            if obj.is_superuser:
                permissions = Permission.objects.none()
                models = [Company, User, CompanyGroup,
                        Commodity, QuestionBank, ProforestForm, ActorType, Category, SubCategory, Topic,
                        MenuPermissions]

                for model in models:
                    content_type = ContentType.objects.get_for_model(model)
                    permissions |= Permission.objects.filter(
                        content_type=content_type)

                for perm in permissions:
                    if perm.content_type.model not in dict:
                        dict[perm.content_type.model] = [perm.codename]
                    else:
                        dict[perm.content_type.model].append(perm.codename)
                return dict

        return dict

    def get_subrole_info(self, obj):
        dict = {}
        try:
            dict['id'] = obj.groups.all()[0].id
            dict['name'] = obj.groups.all()[0].name
        except:
            dict['id'] = ''
            dict['name'] = ''
        return dict


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        exclude = (
            'last_login',
            'is_superuser',
            'is_staff',
            'is_active',
            'date_joined',
            'user_permissions',
        )

        model = User

        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'slug': {
                'read_only': True
            },
        }

    def _save_user_password(self, user, password):
        user.set_password(password)
        user.save()
        return user

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super(UserSerializer, self).create(validated_data)

        return self._save_user_password(user, password)

class CollaboratorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')
    group = serializers.SerializerMethodField('get_subrole_info')
    # role = RoleSerializerDetail(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name',
                'group'
                # 'email', 'role', 
                ]

    def get_full_name(self, obj):
        return str(obj.get_full_name())

    def get_subrole_info(self, obj):
        try:
            name = obj.groups.all()[0].name
        except:
            name = "none"

        return name
    


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetFormSerializer(serializers.Serializer):
    password_confirmation = serializers.CharField()
    password = serializers.CharField()


class CreateUserFormSerializer(serializers.ModelSerializer):

    # password = serializers.CharField(
    #     write_only=True, required=True, validators=[validate_password])

    class Meta:
        
        model = User
        fields = [ 
            'password',
            'email',
            'first_name', 'second_name', 'surname', 'second_surname',
            'indicative', 'phone', 'country', 'region', 'city',
            'company'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'slug': {
                'read_only': True
            },
        }

    def _save_user_password(self, user, password):
        user.set_password(password)
        user.save()
        return user

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super(CreateUserFormSerializer, self).create(validated_data)

        return self._save_user_password(user, password)

class SimpleUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']
    def get_full_name(self, obj):
        return str(obj.get_full_name())
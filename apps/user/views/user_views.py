from django.contrib.auth.models import Permission
from apps.user.models import User, Role, PasswordReset
from apps.utils.permissions import CustomDjangoModelPermission
from cities_light.models import Country, Region, SubRegion

from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView

from ..serializers.user_serializers import (UserSerializer, UserSerializerDetail, CollaboratorSerializer,
                                        PasswordResetSerializer, PasswordResetFormSerializer)

from rest_framework import generics
from rest_framework import status

from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from import_export import fields, resources
from io import BytesIO
from xhtml2pdf import pisa
import datetime as dt

from apps.emailcustom.models import EmailTemplate


# =============================================================================
#                   RESOURCE djangorestframework-guardian 0.3.0
# =============================================================================


# =============================================================================
#                           IMPORT - EXPORT RESOURCE
# =============================================================================

class UserResource(resources.ModelResource):
    country = fields.Field(attribute='get_country_display')
    region = fields.Field(attribute='get_region_display')
    city = fields.Field(attribute='get_city_display')

    def dehydrate_status(self, obj):
        if obj.status:
            return _('Active')
        return _('Inactive')

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'second_name',
            'surname',
            'second_surname',
            'phone',
            'country',
            'region',
            'city',
            'status',
        )
        export_order = (
            'email',
            'first_name',
            'second_name',
            'surname',
            'second_surname',
            'phone',
            'country',
            'region',
            'city',
            'status',
        )

    def get_export_headers(self):
        headers = (
            _('Email'),
            _('First Name'),
            _('Second Name'),
            _('Surname'),
            _('Second Surname'),
            _('Phone'),
            _('Country'),
            _('Region'),
            _('City'),
            _('Status'),

        )
        return headers


# =============================================================================
#                           APIREST USER RESOURCE
# =============================================================================
@permission_classes([IsAuthenticated])
class MeApiView(RetrieveAPIView):
    """
        Returns information of the current user
    """
    serializer_class = UserSerializerDetail

    def get_object(self):
        return self.request.user


class UserListApiView(generics.ListAPIView):
    serializer_class = UserSerializerDetail
    permission_classes = [CustomDjangoModelPermission]

    def get_queryset(self):
        # status = self.request.GET.get('status')
        query_name = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')

        if self.request.user.groups.filter(name='SUPERADMINISTRADOR').exists():
            queryset = User.objects.all().exclude(is_staff=True)
        elif self.request.user.groups.filter(name='ADMINISTRADOR').exists():
            queryset = User.objects.filter(role__name= 'CLIENTE').exclude(is_staff=True)
        else:
            queryset = User.objects.filter(id =self.request.user.id).exclude(is_staff=True)

        # if status == 'false':
        #     queryset = queryset.filter(status=False)
        # elif status == 'true':
        #     queryset = queryset.filter(status=True)

        if query_name != None:
            q1 = Q(*[
                Q(('first_name__istartswith', term)) | Q(('second_name__istartswith', term)) | Q(('surname__istartswith', term)) | Q(
                    ('second_surname__istartswith', term)) | Q(('email__istartswith', term))
                for term in query_name.split()
            ])
            q2 = Q(*[
                Q(('first_name__unaccent__icontains', term)) | Q(('second_name__unaccent__icontains', term)) | Q(
                    ('surname__unaccent__icontains', term)) | Q(('second_surname__unaccent__icontains', term)) | Q(('email__unaccent__icontains', term))
                for term in query_name.split()
            ])
            q3 = Q(*[
                Q(('company__name__unaccent__icontains', term)) 
                for term in query_name.split()
            ])

            queryset = queryset.filter(q1).union(queryset.filter(q2)).union(queryset.filter(q3))

        if active:
            if active == 'full_name':
                if direction == '':
                    pass
                elif direction == 'asc':
                    queryset = queryset.order_by('first_name', 'second_name', 'surname', 'second_surname')
                elif direction == 'desc':
                    queryset = queryset.order_by('-first_name', '-second_name', '-surname', '-second_surname')
            else:
                if direction == '':
                    pass
                elif direction == 'asc':
                    queryset = queryset.order_by(active)
                elif direction == 'desc':
                    filter = str('-'+active)
                    queryset = queryset.order_by(filter)
        return queryset


@permission_classes([CustomDjangoModelPermission])
class UserCreateApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get('password')
        instance = serializer.save()
        if instance.role.name == 'CLIENTE':
            users_emails = [instance.email]
            EmailTemplate.send(
            'new_user_client_created',
            {
                'user_name_email': instance.email,
                'password': password,
                'assigned_company': instance.company.name,
            },
            emails = users_emails, 
            )
        else:
            pass # No es tipo cliente


@permission_classes([CustomDjangoModelPermission])
class UserDetailApiView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializerDetail


@permission_classes([CustomDjangoModelPermission])
class UserUpdateApiView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer, *args, **kwargs):
        if serializer.validated_data['status'] == False: #Condiciona la desactivacion
            object = self.get_object()
            if object.groups.filter(name='SUPERADMINISTRADOR').exists() or object.groups.filter(name='ADMINISTRADOR').exists():
                if not self.request.user.groups.filter(name='SUPERADMINISTRADOR').exists():
                    serializer.validated_data['status'] = True #IF not are a superadministrador cannot disable other user
        serializer.save()
        try:
            password =  serializer.validated_data['password']
            user = self.get_object()
            user.set_password(password)
            user.save()
        except:
            pass



class PasswordResetView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        ''' Valida que el email enviado por el usuario sea valido '''
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email=serializer.validated_data.get('email')).first()

        if user:
            password_reset, _ = PasswordReset.objects.get_or_create(user=user)
            password_reset_slug = password_reset.slug

            user.password_reset_mail(
                password_reset_slug=password_reset_slug,
            )

            return Response(
                {
                    'email': serializer.validated_data.get('email')
                },
                201
            )

        return Response(
            {

                "type": "validation_error",
                "errors": [
                    {
                        "code": "not_exists",
                        "detail": "user with this email does not exists.",
                        "attr": "email"
                    }
                ]
            },
            400
        )

class PasswordResetDoneView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        ''' EJECUTA EL CAMBIO DE CLAVE '''
        if request.data.get('password') != request.data.get('password_confirmation'):
            return Response(
                        {
                            "type": "validation_error",
                            "errors": [
                                {   "code": "not_exists",
                                    "detail": "Boot password don't match ",
                                    "attr": "Password "
                                }
                            ] }, 401
                    )

        password_reset = PasswordReset.objects.filter(slug=kwargs.get('slug')).first()

        if not password_reset:
            return Response(
                        {
                            "type": "validation_error",
                            "errors": [
                                {   "code": "not_exists",
                                    "detail": "This link is Useless ",
                                    "attr": "Password Token"
                                }
                            ] }, 401
                    )

        serializer = PasswordResetFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_reset.user.set_password(serializer.validated_data.get('password'))
        password_reset.user.save()
        password_reset.delete()

        return Response(
            status=201
        )

# Enpoint para enviar colaborators al crear un nuevo formulario

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 1000  # the number of items per page
    page_size_query_param = 'page_size'  # query parameter to specify page size
    max_page_size = 1000  # the maximum number of items per page

@permission_classes([IsAuthenticated])
class ListCollaboratorsApi(generics.ListAPIView):
    ''' Listo solo los que puedan add a proforestform y quito el request.user '''
    serializer_class = CollaboratorSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        perm_addproforestform = Permission.objects.get(codename='add_proforestform')
        queryset = User.objects.filter(Q(groups__permissions=perm_addproforestform) | Q(user_permissions=perm_addproforestform)).distinct()
        queryset = queryset.exclude(pk=self.request.user.pk)
        return queryset



# =============================================================================
#                           BACKOFFICE RESOURCE
# =============================================================================
@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.view_user', raise_exception=True), name='dispatch')
class UserListView(ListView):
    template_name = 'user/user/user_list.html'
    url_name = 'user-list'
    model = User
    paginate_by = 25

    def get_queryset(self):
        filter_list = self.request.GET.getlist('filter')
        filters = Q()
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                fields = [
                    'first_name__icontains',
                    'surname__icontains',
                    'email__icontains',
                    'country__name__icontains',
                    'region__name__icontains',
                    'city__name__icontains',
                ]

                for str_field in fields:
                    filters |= Q(**{str_field: filter})

        queryset = User.objects.filter(filters).order_by('email')

        filter_verified = self.request.GET.get('verified')
        if not (filter_verified == '' or filter_verified == None):
            if (filter_verified == '0'):
                queryset = queryset.filter(status=False)

            elif (filter_verified == '1'):
                queryset = queryset.filter(status=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_obj = {
            'value': [],
            'url': ''
        }

        filter_list = self.request.GET.getlist('filter')
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                filter_obj['value'].append(
                    filter
                )
                filter_obj['url'] += '&filter={}'.format(filter)

        filter_verified = self.request.GET.get('verified')
        if not (filter_verified == '' or filter_verified == None):
            filter_obj['filter_verified'] = filter_verified
            filter_obj['url'] += '&verified={}'.format(filter_verified)
        context['filter_verified'] = filter_verified
        context['filter_obj'] = filter_obj
        context['nav_users'] = True

        paginator = context.get('paginator')
        num_pages = paginator.num_pages
        current_page = context.get('page_obj')
        page_no = current_page.number

        if num_pages <= 11 or page_no <= 6:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 12))]
        elif page_no > num_pages - 6:  # case 4
            pages = [x for x in range(num_pages - 10, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 5, page_no + 6)]

        context.update({'pages': pages})
        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.view_user', raise_exception=True), name='dispatch')
class UserListExportView(View):
    url_name = 'user-list-export'

    def _get_pdf_export(self, queryset, file_name):
        template = get_template('user/report/user/user_list.html')
        context = {
            'user_report': self.request.user,
            'object_list': queryset,
            'current_scheme_host': self.request._current_scheme_host,
        }
        html = template.render(context)
        result = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, debug=1)

        return result

    def _get_export_response(self, queryset, format='csv'):
        dataset = UserResource().export(queryset)
        file_name = "users_{}".format(dt.datetime.now().strftime("%d-%m-%Y"))

        if (format == 'csv'):
            dataset_format = dataset.csv
            CONTENT_DISPOSITION = 'attachment; filename="{}.csv"'.format(
                file_name)
            CONTENT_TYPE = 'text/csv'

        elif (format == 'xls'):
            dataset_format = dataset.xls
            CONTENT_DISPOSITION = 'attachment; filename="{}.xls"'.format(
                file_name)
            CONTENT_TYPE = 'application/vnd.ms-excel'

        elif (format == 'xlsx'):
            dataset_format = dataset.xlsx
            CONTENT_DISPOSITION = 'attachment; filename="{}.xlsx"'.format(
                file_name)
            CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        elif (format == 'tsv'):
            dataset_format = dataset.tsv
            CONTENT_DISPOSITION = 'attachment; filename="{}.tsv"'.format(
                file_name)
            CONTENT_TYPE = 'text/tab-separated-values'

        elif (format == 'ods'):
            dataset_format = dataset.ods
            CONTENT_DISPOSITION = 'attachment; filename="{}.ods"'.format(
                file_name)
            CONTENT_TYPE = 'application/vnd.oasis.opendocument.spreadsheet'

        elif (format == 'json'):
            dataset_format = dataset.json
            CONTENT_DISPOSITION = 'attachment; filename="{}.json"'.format(
                file_name)
            CONTENT_TYPE = 'application/json'

        elif (format == 'yaml'):
            dataset_format = dataset.yaml
            CONTENT_DISPOSITION = 'attachment; filename="{}.yaml"'.format(
                file_name)
            CONTENT_TYPE = 'text/yaml'

        elif (format == 'html'):
            dataset_format = dataset.html
            CONTENT_DISPOSITION = 'attachment; filename="{}.html"'.format(
                file_name)
            CONTENT_TYPE = 'text/html'

        elif (format == 'pdf'):
            result = self._get_pdf_export(queryset, file_name)
            CONTENT_DISPOSITION = 'attachment; filename="{}.pdf"'.format(
                file_name)
            CONTENT_TYPE = 'application/pdf'

            response = HttpResponse(content_type=CONTENT_TYPE)
            response['Content-Disposition'] = CONTENT_DISPOSITION
            response.content = result.getvalue()
            return response

        else:
            dataset_format = dataset.csv
            CONTENT_DISPOSITION = 'attachment; filename="_{}.csv"'.format(
                file_name)
            CONTENT_TYPE = 'text/csv'

        response = HttpResponse(dataset_format, content_type=CONTENT_TYPE)
        response['Content-Disposition'] = CONTENT_DISPOSITION
        return response

    def post(self, request, *args, **kwargs):
        format_file_available = {
            '0': 'csv',
            '1': 'xls',
            '2': 'xlsx',
            '3': 'pdf',
            # '4': 'ods',
            # '5': 'json',
            # '6': 'yaml',
            # '7': 'html',
        }

        id_seleccion = request.POST.getlist('_action_selection')
        action = request.POST.get('_action')
        selected_all_elements = request.POST.get('selected-all-elements')
        format_file_id = request.POST.get('_format_file')
        try:
            format_file = format_file_available[format_file_id]
        except:
            format_file = format_file_available['0']

        if (selected_all_elements == '1' or selected_all_elements == 1):
            queryset = User.objects.all().order_by('email')
            filter_verified = request.POST.get('filter_verified')
            if not (filter_verified == '' or filter_verified == None):
                if (filter_verified == '0'):
                    queryset = queryset.filter(verified=False, rejected=False)

                elif (filter_verified == '1'):
                    queryset = queryset.filter(verified=True, rejected=False)

                elif (filter_verified == '2'):
                    queryset = queryset.filter(verified=False, rejected=True)

            filter_list = request.POST.getlist('filter')
            filters = Q()
            if (filter_list and filter_list != ''):
                for filter in filter_list:
                    fields = [
                        'email__icontains',
                        'country__icontains',
                        'region__icontains',
                        'email__icontains',
                        'city__icontains',
                    ]

                    for str_field in fields:
                        filters |= Q(**{str_field: filter})

                queryset = queryset.filter(filters)

        else:
            if not (id_seleccion == '' or id_seleccion == None):
                queryset = User.objects.filter(
                    id__in=id_seleccion).order_by('email')
            else:
                queryset = User.objects.none()

        response = self._get_export_response(queryset, format=format_file)

        return response

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.add_user', raise_exception=True), name='dispatch')
class UserAddView(CreateView):
    template_name = 'user/user/user_create.html'
    url_name = 'user-add'
    model = User
    fields = [
        'email', 'status', 'first_name', 'second_name', 'surname', 'second_surname',
        'company', 'phone', 'country', 'region', 'city',
        'role', 'password', 'company',
    ]

    def form_valid(self, form):
        object = form.save()

        id_group = self.request.POST.get('group')

        if not (id_group == '' or id_group == None):
            group_selected = Group.objects.get(pk=id_group)
            object.groups.add(group_selected)

        password = self.request.POST.get('password')
        if not (password == '' or password == None):
            object.set_password(password)

        object.save()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.object.pk
        return reverse_lazy("user-detail", kwargs={"pk": pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_group = self.request.POST.get('group')
        if not (id_group == '' or id_group == None):
            group_selected = Group.objects.get(pk=id_group)
            context['group_selected'] = group_selected
        context['roles'] = Role.objects.all()
        context['nav_users'] = True
        context['countries'] = Country.objects.all()

        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.view_user', raise_exception=True), name='dispatch')
class UserDetailView(DetailView):
    template_name = 'user/user/user_detail.html'
    url_name = 'user-detail'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.change_user', raise_exception=True), name='dispatch')
class UserUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'user/user/user_update.html'
    url_name = 'user-update'
    model = User
    success_message = 'User Updated !!!!'
    fields = [
        'email', 'first_name', 'second_name', 'surname', 'second_surname',
        'phone', 'company', 'country', 'region', 'city',
        'status', 'role'
    ]

    def form_valid(self, form):
        object = form.save()

        id_group = self.request.POST.get('group')

        if not (id_group == '' or id_group == None):
            object.groups.clear()
            group_selected = Group.objects.get(pk=id_group)
            object.groups.add(group_selected)

        object.save()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("user-detail", kwargs={"pk": pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['group_selected'] = self.object.groups.all()[0]
        except:
            context['group_selected'] = ''
        context['countries'] = Country.objects.all()
        context['regions'] = Region.objects.filter(country=self.object.country)
        context['cities'] = SubRegion.objects.filter(
            country=self.object.country, region=self.object.region)
        context['groups'] = Group.objects.all()
        context['roles'] = Role.objects.all()
        context['nav_users'] = True
        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.delete_user', raise_exception=True), name='dispatch')
class UserDeleteView(View):
    url_name = 'user-delete'

    def post(self, request,):
        user = get_object_or_404(User, pk=self.request.POST['pk'])
        try:
            user.delete()
            response = {
                'status': 'success',
                'title': _('Successful removal!'),
                'message': _('User has been deleted!')
            }
        except:
            response = {
                'status': 'error',
                'title': _('Failed Delete!'),
                'message': _('The item has history and cannot be deleted!')
            }
        return JsonResponse(response)

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('user.change_user', raise_exception=True), name='dispatch')
class UserDeactivateView(View):
    url_name = 'user-deactivate'

    def post(self, request,):
        user = get_object_or_404(User, pk=self.request.POST['pk'])
        if (user.status):
            user.status = False
            title = _('Successful deactivation')
            message = _('User has been disabled!')
            user.save()
        else:
            user.status = True
            title = _('Successful activation')
            message = _('User has been reactivated!')
            user.save()

        response = {
            'status': 'success',
            'title': title,
            'message': message
        }

        return JsonResponse(response)


@permission_classes([CustomDjangoModelPermission])
class UserDestroy(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.status = False
            instance.save()
            return Response(data={}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_destroy",
                            "detail": "User cannot be destroy it is asociated to other models.",
                            "attr": "User"
                        }
                    ]
                },
                403
            )

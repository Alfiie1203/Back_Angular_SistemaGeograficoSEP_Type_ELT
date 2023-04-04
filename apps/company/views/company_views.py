from apps.utils.permissions import CustomDjangoModelPermission
from apps.supplybase.models.supplybase import SupplyBaseDependency

from cities_light.models import Country, Region, SubRegion
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.template.loader import get_template

from ..models.company import Company, ProforestCode
from ..models.commodity import Commodity
from ..models.actor_type import ActorType

from ..serializers.company_serializer import CompanySerializer, CompanySerializerDetail

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from io import BytesIO
from xhtml2pdf import pisa
from import_export import fields, resources
import datetime as dt


def check_user_groups(user, groups):
    return user.groups.filter(Q(name__in=groups)).exists()

# =============================================================================
#                           IMPORT - EXPORT RESOURCE
# =============================================================================
from django.utils import translation

class CompanyResource(resources.ModelResource):
    #Search the name_en translation to return name in the language of the loged User
    def dehydrate_commodity(self, obj):
        name_translate = 'name_'+ str(translation.get_language())
        return getattr(obj.commodity, name_translate)

    def dehydrate_actor_type(self, obj):
        name_translate = 'name_'+ str(translation.get_language())
        return getattr(obj.actor_type, name_translate)

    def dehydrate_country(self, obj):
        if obj.country:
            return obj.country.name
        return _('No Register')

    def dehydrate_region(self, obj):
        if obj.region:
            return obj.region.name
        return _('No Register')

    def dehydrate_city(self, obj):
        if obj.city:
            return obj.city.name
        return _('No Register')

    def dehydrate_company_group(self, obj):
        return obj.company_group.name


    def dehydrate_validator_user(self, obj):
        return obj.validator_user

    def dehydrate_status(self, obj):
        if obj.status:
            return _('Active')
        return _('Inactive')

    class Meta:
        model = Company
        fields = (
            'name_en',
            'nit',
            'identifier_proforest_company',
            'identifier_global_company',
            'commodity',
            'actor_type',
            'country',
            'region',
            'city',
            'latitude',
            'longitude',
            'company_group',
            'company_profile',
            'validator_user',
            'status_revision',
            'status',
        )
        export_order = (
            'name_en',
            'nit',
            'identifier_proforest_company',
            'identifier_global_company',
            'commodity',
            'actor_type',
            'country',
            'region',
            'city',
            'latitude',
            'longitude',
            'company_group',
            'company_profile',
            'validator_user',
            'validated',
            'status',

        )

    def get_export_headers(self):
        headers = (
            _('Name'),
            _('Nit'),
            _('Proforest Company Identifier'),
            _('Global Identifier'),
            _('Commodity'),
            _('Actor Type'),
            _('Country'),
            _('Region'),
            _('City'),
            _('Latitude'),
            _('Longitude'),
            _('Business Group'),
            _('Company Profile'),
            _('Manager User'),
            _('Validator User'),
            _('Status Revision'),
            _('Status'),
        )
        return headers

# =============================================================================
#                           APIREST RESOURCE
# =============================================================================


@permission_classes([CustomDjangoModelPermission])
class CompanyList(generics.ListAPIView):
    serializer_class = CompanySerializerDetail

    def get_queryset(self):
        queryset = Company.objects.all()

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)

        name = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')

        if name != None and name !='':
            queryset = queryset.filter(name__unaccent__icontains=name)
        if active:
            if direction == '':
                pass
            elif direction == 'asc':
                queryset = queryset.order_by(active)
            elif direction == 'desc':
                filter = str('-'+active)
                queryset = queryset.order_by(filter)

        if self.request.user.has_perm('company.update_own_company'):
            try:
                queryset = Company.objects.filter(pk=self.request.user.company.pk)
            except:
                pass
        groups = ['VERIFICADOR', 'VALIDADOR']
        if check_user_groups(self.request.user, groups):
            queryset = Company.objects.none()

        return queryset


@permission_classes([IsAuthenticated])
class CompanySearch(generics.ListAPIView):
    serializer_class = CompanySerializerDetail

    def get(self, request):
        name = self.request.GET.get('name')
        if name != None:
            queryset = Company.objects.filter(
                Q(name__unaccent__icontains=name))[:5]
        else:
            queryset = Company.objects.all()
        array = []
        for a in queryset:
            array.append(a.name)
        return Response({'results': array})


@permission_classes([CustomDjangoModelPermission])
class CompanyCreate(generics.CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


@permission_classes([CustomDjangoModelPermission])
class CompanyView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerDetail


@permission_classes([CustomDjangoModelPermission])
class CompanyUpdate(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


@permission_classes([CustomDjangoModelPermission])
class CompanyDestroy(generics.DestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_destroy",
                            "detail": "Company cannot be deleted it is asociated to other models.",
                            "attr": "Company"
                        }
                    ]
                },
                403
            )

@permission_classes([CustomDjangoModelPermission])
class CompanyDelete(APIView):
    queryset = Company.objects.all()

    def get(self, request, *args, **kwargs):
        id_proforest_company = self.request.GET.get('id_proforest_company')
        try:
            company = Company.objects.get(identifier_proforest_company = id_proforest_company)
            serializer = CompanySerializerDetail(company)
            return Response(serializer.data)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "not_found",
                            "detail": "Company with this code does not exists",
                            "attr": "Company"
                        }
                    ]
                },
                404
            )
    def post(self, request, *args, **kwargs):
        id_proforest_company = self.request.GET.get('id_proforest_company')
        company = Company.objects.get(identifier_proforest_company = id_proforest_company)

        try:
            company.delete()
            return Response(data='erased company', status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_destroy",
                            "detail": "Company cannot be deleted it is asociated to other models.",
                            "attr": "Company"
                        }
                    ]
                },
                403
            )

@permission_classes([IsAuthenticated])
class PreviousProforestCode(APIView):
    def get(self, request, format=None):
        """
        Return a tentative code.
        """
        actor_type_pk = request.query_params['actor_type']
        commodity_pk = request.query_params['commodity']
        abc = ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
               "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

        if ProforestCode.objects.exists():
            pkey = ProforestCode.objects.latest('id').pk + 1
        else:
            pkey = 1
        try:
            actor_type = ActorType.objects.get(
                pk=actor_type_pk).proforest_actortype_code
            commodity = Commodity.objects.get(
                pk=commodity_pk).proforest_commodity_code
            if pkey <= 99999999:
                code = str(pkey).zfill(8)
                if len(code) < 2:
                    code = code.zfill(7)
                else:
                    code = code.zfill(6)
            else:
                index = pkey // 100000000
                code = str(pkey - (100000000*(pkey//100000000)))
                if len(code) < 2:
                    code = code.zfill(7)
                else:
                    code = code.zfill(6)
                code = abc[index] + code

            proforestcode = str(actor_type+commodity+'-'+code)

            return Response({'ProforestCode': proforestcode})
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)


@permission_classes([IsAuthenticated])
class CompanyListCreateUserForm(generics.ListAPIView):
    serializer_class = CompanySerializerDetail

    def get_queryset(self):
        status = self.request.GET.get('status')
        queryset = Company.objects.all()
        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)

        return queryset

# =============================================================================
#                           BACKOFFICE RESOURCE
# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.view_company', raise_exception=True), name='dispatch')
class CompanyListView(ListView):
    template_name = 'company/company/company_list.html'
    url_name = 'company-list'
    model = Company
    paginate_by = 25

    def get_queryset(self):
        filter_list = self.request.GET.getlist('filter')
        filters = Q()
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                fields = [
                    'name__icontains',
                    'identifier_global_company__icontains',
                    'nit__icontains',
                    'country__name__icontains',
                    'region__name__icontains',
                    'city__name__icontains'
                ]

                for str_field in fields:
                    filters |= Q(**{str_field: filter})

        queryset = Company.objects.filter(filters).order_by('-id')

        filter_status_company = self.request.GET.get('status_company')
        if not (filter_status_company == '' or filter_status_company == None):
            if (filter_status_company == '0'):
                queryset = queryset.filter(status=False)

            elif (filter_status_company == '1'):
                queryset = queryset.filter(status=True)

            # elif (filter_verified == '2'):
            #     queryset = queryset.filter(verified=False, rejected=True)

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

        filter_status_company = self.request.GET.get('status_company')
        if not (filter_status_company == '' or filter_status_company == None):
            filter_obj['filter_status_company'] = filter_status_company
            filter_obj['url'] += '&verified={}'.format(filter_status_company)
        context['filter_status_company'] = filter_status_company
        context['filter_obj'] = filter_obj
        context['nav_company'] = True

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


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.add_company', raise_exception=True), name='dispatch')
class CompanyCreateView(CreateView):
    template_name = 'company/company/company_create.html'
    url_name = 'company-create'
    model = Company
    fields = [
        'name', 'identifier_global_company', 'nit', 'country', 'region', 'city',
        'latitude', 'longitude', 'company_group', 'actor_type', 'commodity'
    ]

    def get_success_url(self):
        pk = self.object.pk
        return reverse_lazy("company-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        context['nav_company'] = True
        context['commodities'] = Commodity.objects.filter(status=True)
        context['actor_types'] = ActorType.objects.filter(status=True)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.view_company', raise_exception=True), name='dispatch')
class UserDetailView(DetailView):
    template_name = 'company/company/company_detail.html'
    url_name = 'company-detail'
    model = Company


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_company', raise_exception=True), name='dispatch')
class CompanyUpdateView(UpdateView):
    template_name = 'company/company/company_update.html'
    url_name = 'company-update'
    model = Company
    fields = [
        'identifier_proforest_company', 'name', 'country', 'region', 'city', 'latitude', 'longitude', 'identifier_global_company',
        'nit', 'company_group', 'validator_user', 'company_profile',  'status',
        'status_revision',
    ]

    def get_success_url(self):
        return reverse_lazy("company-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name_translate = 'name_'+ str(translation.get_language())

        context['countries'] = Country.objects.all()
        context['regions'] = Region.objects.filter(
            country=self.object.country)
        context['cities'] = SubRegion.objects.filter(
            country=self.object.country, region=self.object.region)
        context['nav_company'] = True
        context['commodity_name'] = getattr(self.get_object().commodity, name_translate)
        context['actor_type_name'] = getattr(self.get_object().actor_type, name_translate)

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_company', raise_exception=True), name='dispatch')
class CompanyDeactivateView(View):
    url_name = 'company-deactivate'

    def post(self, request,):
        company = get_object_or_404(Company, pk=self.request.POST['pk'])
        message = _('Activation')
        if (company.status):
            company.status = False
            message = _('Deactivation')
            company.save()
        else:
            company.status = True
            company.save()

        response = {
            'status': 'success',
            'title':  _(u"Successful {message}").format(message=message),
        }

        return JsonResponse(response)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.delete_company', raise_exception=True), name='dispatch')
class CompanyDeleteView(View):
    url_name = 'company-delete'

    def post(self, request,):
        company = get_object_or_404(Company, pk=self.request.POST['pk'])
        try:
            company.delete()
            response = {
                'status': 'success',
                'title': _('Successful removal!'),
            }
        except:
            response = {
                'status': 'error',
                'title': _('Failed Delete!'),
                'message': _('The item has history and cannot be deleted!')
            }
        return JsonResponse(response)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.view_company', raise_exception=True), name='dispatch')
class CompanyExportView(View):
    url_name = 'company-export'

    def _get_pdf_export(self, queryset, file_name):
        template = get_template('report/company/company_list.html')
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
        dataset = CompanyResource().export(queryset)
        file_name = "company_{}".format(dt.datetime.now().strftime("%d-%m-%Y"))

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
            queryset = Company.objects.all().order_by('name')
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
                        'name__icontains',
                    ]

                    for str_field in fields:
                        filters |= Q(**{str_field: filter})

                queryset = queryset.filter(filters)

        else:
            if not (id_seleccion == '' or id_seleccion == None):
                queryset = Company.objects.filter(
                    id__in=id_seleccion).order_by('name')
            else:
                queryset = Company.objects.none()

        response = self._get_export_response(queryset, format=format_file)

        return response


@permission_classes([IsAuthenticated]) #Para crear trazabilidad
class CompanySearchDetail(generics.ListAPIView):
    serializer_class = CompanySerializerDetail


    def get_queryset(self):
        if self.request.user.role.name == 'CLIENTE': #Return just reported by my company
            reported_company = self.request.user.company
            try:
                actortypes = SupplyBaseDependency.objects.get(actor_type = reported_company.actor_type).actor_type_dependency.all()
                queryset = Company.objects.filter(actor_type__in=actortypes, status=True)
                queryset = queryset.exclude(id = reported_company.id)
            except:
                queryset = Company.objects.filter(id=1).none()
        else:
            queryset = Company.objects.filter(status=True)

        name = self.request.GET.get('name')
        queryset = queryset.filter(
                Q(name__unaccent__icontains=name))[:10]
        return queryset

@permission_classes([IsAuthenticated]) #Para crear trazabilidad
class CompanySearchPlantillaXlsx(generics.ListAPIView):
    serializer_class = CompanySerializerDetail


    def get_queryset(self):
        if self.request.user.role.name == 'CLIENTE': #Return just reported by my company
            reported_company = self.request.user.company
            actortypes = SupplyBaseDependency.objects.get(actor_type = reported_company.actor_type).actor_type_dependency.all()
            queryset = Company.objects.filter(actor_type__in=actortypes)
        else:
            #traigo los que tiene SupplyBase dependency
            actortype_enabled = SupplyBaseDependency.objects.all().values_list('actor_type', flat=True)
            queryset = Company.objects.filter(actor_type__in =actortype_enabled)
        name = self.request.GET.get('name')
        queryset = queryset.filter(
                Q(name__unaccent__icontains=name))[:10]
        return queryset
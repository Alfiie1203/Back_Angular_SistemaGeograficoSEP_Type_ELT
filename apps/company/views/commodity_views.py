from apps.utils.permissions import CustomDjangoModelPermission
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.template.loader import get_template

from ..models.commodity import Commodity
from ..serializers.commodity_serializer import CommoditySerializer, CommoditySerializerDetail

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from io import BytesIO
from xhtml2pdf import pisa
from import_export import resources
import datetime as dt

# =============================================================================
#                           IMPORT - EXPORT RESOURCE
# =============================================================================

from django.utils import translation

class CommodityResource(resources.ModelResource):

    #Search the name_en translation to return name in the language of the loged User
    def dehydrate_name_en(self, obj):
        name_trans = 'name_'+ str(translation.get_language())
        return getattr(obj, name_trans)

    def dehydrate_status(self, obj):
        if obj.status:
            return _('Active')
        return _('Inactive')

    class Meta:
        model = Commodity
        fields = (
            'name_en',
            'proforest_commodity_code',
            'status',
        )
        export_order = (
            'name_en',
            'proforest_commodity_code',
            'status',
        )

    def get_export_headers(self):
        headers = (
            _('Name'),
            _('Code'),
            _('Status'),
        )
        return headers

# =============================================================================
#                    APIREST Commodity RESOURCE
# =============================================================================


@permission_classes([CustomDjangoModelPermission])
class CommodityList(generics.ListAPIView):
    serializer_class = CommoditySerializer

    def get_queryset(self):
        queryset = Commodity.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')
        language_code = self.request.headers.get('Content-Language')

        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)
        if search != None:
            fields = [
                f'name_{language_code}__icontains',
                'proforest_commodity_code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')

        if active:
            if active == 'name':
                active = f'name_{language_code}'
            if direction == '':
                pass
            elif direction == 'asc':
                queryset = queryset.order_by(active)
            elif direction == 'desc':
                filter = str('-'+active)
                queryset = queryset.order_by(filter)
        return queryset
    
    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context


@permission_classes([IsAuthenticated])
class CommodityListCreateCompanyForm(generics.ListAPIView):
    serializer_class = CommoditySerializer

    def get_queryset(self):
        status = self.request.GET.get('status')
        queryset = Commodity.objects.all()
        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)

        if self.request.user.role.name=='COLABORADOR':
            #devuelvo todos los commodities
            return queryset
        else: #solo a los que la compañia a la que pertenesca el usuario pueda comprarle
            commodity_cliente = self.request.user.company.commodity
            queryset = queryset.filter(id = commodity_cliente.id)
            return queryset

    
    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context


@permission_classes([CustomDjangoModelPermission])
class CommodityCreate(generics.CreateAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context


@permission_classes([CustomDjangoModelPermission])
class CommodityView(generics.RetrieveAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializerDetail


@permission_classes([IsAuthenticated])
class CommodityViewCreateCompanyForm(generics.RetrieveAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializerDetail


@permission_classes([CustomDjangoModelPermission])
class CommodityUpdate(generics.UpdateAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context


@permission_classes([CustomDjangoModelPermission])
class CommodityDestroy(generics.DestroyAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer

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
                            "detail": "Commodity cannot be deleted it is asociated to other models.",
                            "attr": "Commodity"
                        }
                    ]
                },
                403
            )


@permission_classes([IsAuthenticated])
class CommoditySearch(generics.ListAPIView):
    serializer_class = CommoditySerializerDetail

    def get(self, request):
        search = self.request.GET.get('name')
        language_code = self.request.headers.get('Content-Language')
        

        if search != None:
            fields = [
                'name_es__icontains',
                'name_en__icontains',
                'name_pt__icontains',
                'proforest_commodity_code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = Commodity.objects.filter(filters).order_by('id')[:5]
        
        else:
            queryset = Commodity.objects.all()[:5]
        array = []
        for commodity in queryset:
            array.append(getattr(commodity, 'name_en'))
            array.append(getattr(commodity, 'name_es'))
            array.append(getattr(commodity, 'name_pt'))

        return Response({'results': array})

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.view_commodity', raise_exception=True), name='dispatch')
class CommodityListView(ListView):
    template_name = 'company/commodity/commodity_list.html'
    url_name = 'commodity-list'
    model = Commodity
    paginate_by = 25

    def get_queryset(self):
        language_code = translation.get_language()
        filter_list = self.request.GET.getlist('filter')
        filters = Q()
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                fields = [
                    f'name_{language_code}__icontains',
                    'proforest_commodity_code__icontains',
                ]

                for str_field in fields:
                    filters |= Q(**{str_field: filter})

        queryset = Commodity.objects.filter(filters).order_by('-id')

        filter_status = self.request.GET.get('status')
        if not (filter_status == '' or filter_status == None):
            if (filter_status == '0'):
                queryset = queryset.filter(status=False)

            elif (filter_status == '1'):
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

        filter_status = self.request.GET.get('status')
        if not (filter_status == '' or filter_status == None):
            filter_obj['filter_status'] = filter_status
            filter_obj['url'] += '&verified={}'.format(filter_status)
        context['filter_status'] = filter_status
        context['filter_obj'] = filter_obj
        context['nav_commodity'] = True

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
@method_decorator(permission_required('company.add_commodity', raise_exception=True), name='dispatch')
class CommodityCreateView(CreateView):
    template_name = 'company/commodity/commodity_create.html'
    url_name = 'commodity-create'
    model = Commodity
    fields = [
        'name_es',
        'name_en',
        'name_pt',
        'proforest_commodity_code'
    ]

    def get_success_url(self):
        return reverse_lazy("commodity-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_commodity'] = True
        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_commodity', raise_exception=True), name='dispatch')
class CommodityUpdateView(UpdateView):
    template_name = 'company/commodity/commodity_update.html'
    url_name = 'commodity-update'
    model = Commodity
    fields = [
        'name_es',
        'name_en',
        'name_pt',
        'proforest_commodity_code',
        'status'
    ]

    def get_success_url(self):
        return reverse_lazy("commodity-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_commodity'] = True
        return context

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_commodity', raise_exception=True), name='dispatch')
class CommodityDeactivateView(View):
    url_name = 'commodity-deactivate'

    def post(self, request,):
        commodity = get_object_or_404(Commodity, pk=self.request.POST['pk'])
        message = _('Activation')
        if (commodity.status):
            commodity.status = False
            message = _('Deactivation')
            commodity.save()
        else:
            commodity.status = True
            commodity.save()

        response = {
            'status': 'success',
            'title':  _(u"Successful {message}").format(message=message),
        }

        return JsonResponse(response)

# =============================================================================

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_commodity', raise_exception=True), name='dispatch')
class GetActorTypeByCommodity(View):
    url_name = 'get-actor-type-by-commodity'

    def post(self, request,):
        commodity = get_object_or_404(Commodity, pk=self.request.POST['pk'])
        message = _('Activation')
        if (commodity.status):
            commodity.status = False
            message = _('Deactivation')
            commodity.save()
        else:
            commodity.status = True
            commodity.save()

        response = {
            'status': 'success',
            'title':  _(u"Successful {message}").format(message=message),
        }

        return JsonResponse(response)

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.delete_commodity', raise_exception=True), name='dispatch')
class CommodityDeleteView(View):
    url_name = 'commodity-delete'

    def post(self, request,):
        commodity = get_object_or_404(Commodity, pk=self.request.POST['pk'])
        try:
            commodity.delete()
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

# =============================================================================


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.view_commodity', raise_exception=True), name='dispatch')
class CommodityExportView(View):
    url_name = 'commodity-export'

    def _get_pdf_export(self, queryset, file_name):
        template = get_template('report/commodity/commodity_list.html')
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
        dataset = CommodityResource().export(queryset)
        file_name = "commodity_{}".format(
            dt.datetime.now().strftime("%d-%m-%Y"))

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
            queryset = Commodity.objects.all().order_by('id')
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
                queryset = Commodity.objects.filter(
                    id__in=id_seleccion).order_by('id')
            else:
                queryset = Commodity.objects.none()

        response = self._get_export_response(queryset, format=format_file)

        return response

# =============================================================================

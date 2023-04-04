from apps.company.models.actor_type import ActorType
from apps.company.models.commodity import Commodity

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import translation


from ..models.supplybase import SupplyBase, SupplyBaseDependency

# =============================================================================
#                           BACKOFFICE RESOURCE
# =============================================================================


@method_decorator(login_required, name='dispatch')
class SupplybasedependencyList(ListView):
    template_name = 'supplybase/supplybase_list.html'
    url_name = 'supplybase-dependency-list'
    model = SupplyBaseDependency
    paginate_by = 25

    def get_queryset(self):
        name_translate = 'name_'+ str(translation.get_language())
        filter_list = self.request.GET.getlist('filter')
        filters = Q()
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                fields = [
                    'actor_type__'+name_translate+'__icontains',
                    'actor_type_dependency__'+name_translate+'__icontains',
                ]

                for str_field in fields:
                    filters |= Q(**{str_field: filter})
        queryset = SupplyBaseDependency.objects.filter(filters).order_by('-id')

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

        
        context['filter_obj'] = filter_obj
        context['nav_supplybasedependency'] = True

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
@method_decorator(permission_required('company.add_supplybase', raise_exception=True), name='dispatch')
class SupplybasedependencyCreate(CreateView):
    template_name = 'supplybase/supplybase_create.html'
    url_name = 'supplybase-dependency-create'
    model = SupplyBaseDependency
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy("supplybase-dependency-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name_translate = 'name_'+ str(translation.get_language())
        commodities = Commodity.objects.filter(status=True)
        context['commodities'] = commodities
        optgroups = []

        for commodity in commodities:
            commodity_optgroup = {
                "label": getattr(commodity, name_translate),
                "options": []
            }
            dependencies = ActorType.objects.filter(status=True, commodity= commodity)
            
            for dependency in dependencies:
                commodity_optgroup["options"].append({
                    "value": dependency.id,
                    "name": getattr(dependency, name_translate),
                })
            optgroups.append(commodity_optgroup)
        context['optgroups'] = optgroups

        filter_translate = 'commodity__name_'+ str(translation.get_language())
        queryset = ActorType.objects.none()
        for commodity in commodities:
            queryset |= ActorType.objects.filter(status=True, commodity= commodity)
        context['actor_types'] = queryset.order_by(filter_translate)
        context['nav_supplybase'] = True

        return context
# =============================================================================

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('company.change_supplybase', raise_exception=True), name='dispatch')
class SupplybasedependencyUpdate(UpdateView):
    template_name = 'supplybase/supplybase_update.html'
    url_name = 'supplybase-dependency-update'
    model = SupplyBaseDependency
    fields = [ 'actor_type_dependency']

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("supplybase-dependency-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplybaseDependency = SupplyBaseDependency.objects.get(pk=self.kwargs["pk"])
        name_translate = 'commodity__name_'+ str(translation.get_language())
        commodities = Commodity.objects.filter(status=True)
        queryset = ActorType.objects.none()
        for commodity in commodities:
            queryset |= ActorType.objects.filter(status=True, commodity= commodity)
        context['actor_types'] = queryset.order_by(name_translate)
        context['supplybaseDependency'] = supplybaseDependency
        context['dependencies'] = supplybaseDependency.actor_type_dependency.all()
        context['nav_supplybase'] = True
        return context

# =============================================================================

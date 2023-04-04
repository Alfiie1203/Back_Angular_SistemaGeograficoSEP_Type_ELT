from ..models import EmailTemplate

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import translation


@method_decorator(login_required, name='dispatch')
class EmailTemplateList(ListView):
    template_name = 'emailcustom/emailtemplate-list.html'
    url_name = 'emailtemplate-list'
    model = EmailTemplate
    paginate_by = 25

    def get_queryset(self):
        name_translate = 'name_'+ str(translation.get_language())
        filter_list = self.request.GET.getlist('filter')
        filters = Q()
        if (filter_list and filter_list != ''):
            for filter in filter_list:
                fields = [
                    'subject__icontains',
                    'from_email__icontains',
                    'template_key__icontains',

                ]

                for str_field in fields:
                    filters |= Q(**{str_field: filter})
        queryset = EmailTemplate.objects.filter(filters).order_by('-id')

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
        context['nav_emailtemplate'] = True

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
@method_decorator(permission_required('company.change_supplybase', raise_exception=True), name='dispatch')
class EmailTemplateUpdate(UpdateView):
    template_name = 'emailcustom/emailtemplate_update.html'
    url_name = 'emailtemplate-update'
    model = EmailTemplate
    fields = [ 'subject', 'from_email', 'html_template', 'template_key']

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("emailtemplate-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emailTemplate = EmailTemplate.objects.get(pk=self.kwargs["pk"])
        context['emailTemplate'] = emailTemplate
        context['nav_emailtemplate'] = True
        return context

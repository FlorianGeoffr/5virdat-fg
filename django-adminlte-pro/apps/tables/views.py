import json, csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from apps.common.models import * # all models 
from apps.common.forms  import * # all forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from apps.tables.utils import product_filter
from django.conf import settings
from django.urls import reverse
from django.views import View
from helpers import * 

# Create your views here.

def create_filter(request):
    if request.method == "POST":
        keys = request.POST.getlist('key')
        values = request.POST.getlist('value')
        for i in range(len(keys)):
            key = keys[i]
            value = values[i]

            ModelFilter.objects.update_or_create(
                parent=ModelChoices.ITEMS,
                key=key,
                defaults={'value': value}
            )

        return redirect(request.META.get('HTTP_REFERER'))

def create_page_items(request):
    if request.method == 'POST':
        items = request.POST.get('items')
        page_items, created = PageItems.objects.update_or_create(
            parent=ModelChoices.ITEMS,
            defaults={'items_per_page':items}
        )
        return redirect(request.META.get('HTTP_REFERER'))

def create_hide_show_filter(request):
    if request.method == "POST":
        data_str = list(request.POST.keys())[0]
        data = json.loads(data_str)

        HideShowFilter.objects.update_or_create(
            parent=ModelChoices.ITEMS,
            key=data.get('key'),
            defaults={'value': data.get('value')}
        )

        response_data = {'message': 'Model updated successfully'}
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def delete_filter(request, id):
    filter_instance = ModelFilter.objects.get(id=id, parent=ModelChoices.ITEMS)
    filter_instance.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def datatables_apps(request):

    DT_MODEL, DT_MODEL_FORM = get_active_model( request )

    # Submit data: Create/update or Change Model
    if request.method == 'POST':

        active_model = request.POST.get('active_model', None)    
        if active_model:
            request.session['active_model'] = active_model
            return redirect(request.META.get('HTTP_REFERER'))
        else:    
            form = DT_MODEL_FORM(request.POST)
            if form.is_valid():
                return post_request_handling(request, form)    
    
    db_field_names = [field.name for field in DT_MODEL._meta.get_fields()]

    # hide show column
    field_names = []
    for field_name in db_field_names:
        fields, created = HideShowFilter.objects.get_or_create(key=field_name, parent=ModelChoices.ITEMS)
        if fields.key in db_field_names:  # Ensure field exists in MODEL
            field_names.append(fields)

    # model filter
    filter_string = {}
    filter_instance = ModelFilter.objects.filter(parent=ModelChoices.ITEMS)
    for filter_data in filter_instance:
        if filter_data.key in db_field_names:  # Ensure filter key exists in MODEL
            filter_string[f'{filter_data.key}__icontains'] = filter_data.value

    order_by = request.GET.get('order_by', 'ID')
    if order_by not in db_field_names:  # Ensure order_by field exists in MODEL
        order_by = 'ID'
    
    queryset = DT_MODEL.objects.filter(**filter_string).order_by(order_by)
    product_list = product_filter(request, queryset, db_field_names)
    form = DT_MODEL_FORM()

    # pagination
    page_items = PageItems.objects.filter(parent=ModelChoices.ITEMS).last()
    items = 5
    if page_items:
        items = page_items.items_per_page

    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, items)

    try:
        dbItems = paginator.page(page)
    except PageNotAnInteger:
        return redirect('datatables_apps')
    except EmptyPage:
        return redirect('datatables_apps') 
    
    read_only_fields = ('id', )

    context = {
        'segment'  : 'datatables_apps',
        'parent'   : 'apps',
        'form'     : form,
        'dbItems' : dbItems,
        'total_items': DT_MODEL.objects.count(),
        'db_field_names': db_field_names,
        'field_names': field_names,
        'filter_instance': filter_instance,
        'read_only_fields': read_only_fields,
        'items': items
    }
    
    return render(request, 'pages/apps/datatables_apps.html', context)

@login_required(login_url='/accounts/login/')
def post_request_handling(request, form):
    form.save()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/accounts/login/')
def delete(request, id):
    DT_MODEL, DT_MODEL_FORM = get_active_model( request )
    sale = DT_MODEL.objects.get(ID=id)
    sale.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/accounts/login/')
def update(request, id):
    
    DT_MODEL, DT_MODEL_FORM = get_active_model( request )

    model = DT_MODEL.objects.get(ID=id)
    if request.method == 'POST':
        for attribute, value in request.POST.items():
            if attribute == 'csrfmiddlewaretoken':
                continue

            if getattr(model, attribute, value) is not None:
                setattr(model, attribute, value)
        
        model.save()

    return redirect(request.META.get('HTTP_REFERER'))

# Export as CSV
class ExportCSVView(View):
    def get(self, request):

        DT_MODEL, DT_MODEL_FORM = get_active_model( request )

        db_field_names = [field.name for field in DT_MODEL._meta.get_fields()]
        fields = []
        show_fields = HideShowFilter.objects.filter(value=False, parent=ModelChoices.ITEMS)
        
        # Append only existing fields
        for field in show_fields:
            if field.key in db_field_names:
                fields.append(field.key)
            else:
                # Log or handle non-existent fields
                print(f"Field {field.key} does not exist in model.")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(fields)  # Write the header

        filter_string = {}
        filter_instance = ModelFilter.objects.filter(parent=ModelChoices.ITEMS)
        for filter_data in filter_instance:
            filter_string[f'{filter_data.key}__icontains'] = filter_data.value

        order_by = request.GET.get('order_by', 'ID')
        queryset = DT_MODEL.objects.filter(**filter_string).order_by(order_by)

        products = product_filter(request, queryset, db_field_names)

        for product in products:
            row_data = []
            for field in fields:
                try:
                    row_data.append(getattr(product, field))
                except AttributeError:
                    row_data.append('')  # Add empty value if field does not exist
            writer.writerow(row_data)

        return response

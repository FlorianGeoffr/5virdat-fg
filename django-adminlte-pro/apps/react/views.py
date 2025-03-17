from django.shortcuts import render
from django.core import serializers
from apps.common.models import Sales

# Create your views here.

def charts(request):
    filter_data = {}
    if from_date := request.GET.get('from'):
        filter_data['PurchaseDate__gte'] = from_date
    
    if to_date := request.GET.get('to'):
        filter_data['PurchaseDate__lte'] = to_date

    sales = serializers.serialize('json', Sales.objects.filter(**filter_data))
    context = {
        'segment'  : 'react_charts',
        'parent'   : 'apps',
        'sales': sales
    }
    return render(request, 'pages/apps/react/charts.html', context)
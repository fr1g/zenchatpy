from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


# Create your views here.


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def index(request):
    data = {'k': 'v'}
    return Response(data, template_name="index.html")
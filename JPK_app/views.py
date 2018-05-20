from django.shortcuts import render
from django.views import View
from .models import SprzedazWiersz
import xml.etree.ElementTree as etree

# Create your views here.



tree = etree.parse('JPK/JPK_VAT2_20171015_191844_00c.xml')
root = tree.getroot()

class SprzedazView(View):
    def get(self, request):
        sprzedaz = {}
        for row in root.findall('{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}SprzedazWiersz'):
            for element in row:
                sprzedaz[element.tag[element.tag.index('}')+1:]] = element.text
            SprzedazWiersz.objects.create(**sprzedaz)
            sprzedaz.clear()
        ctx = {'sprzedaz': sprzedaz}
        return render(request, 'sprzedaz.html', ctx)

#
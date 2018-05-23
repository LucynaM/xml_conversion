from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest
from .models import SprzedazWiersz, ZakupWiersz
import xml.etree.ElementTree as etree
import django_excel as excel
import xlsxwriter
import collections

# Create your views here.



tree = etree.parse('JPK/JPK_VAT2_20171015_191844_00c.xml')
root = tree.getroot()

class ConvertToDBView(View):
    def get_data(self, search_param, model):
        container = {}
        for row in root.findall(search_param):
            for element in row:
                container[element.tag[element.tag.index('}')+1:]] = element.text
            model.objects.create(**container)
            container.clear()


    def get(self, request):
        self.get_data('{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}SprzedazWiersz', SprzedazWiersz)
        self.get_data('{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}ZakupWiersz', ZakupWiersz)
        test = 'działam'
        ctx = {'test': test}
        return render(request, 'sprzedaz.html', ctx)


class ExportToExcel(View):

    def get_headers(self, obj_keys, query_set):
        container = []
        for el in obj_keys:
            if el not in ['_state', 'id']:
                test_if_empty = len([True for obj in query_set.objects.all() if getattr(obj, el) == None])
                if test_if_empty != query_set.objects.count():
                    container.append(el)
        return container

    def worksheet_generate(self, headers, sheet, keys, query_set, bold, date_fields, date, money_fields, money):
        col = 0
        row = 1
        for el in headers:
            sheet.write(0, col, el, bold)
            col += 1

        for el in query_set.objects.all():
            el_items = collections.OrderedDict(sorted(el.__dict__.items(), key=lambda t: keys.index(t[0])))
            col = 0
            for k, v in el_items.items():
                if k in headers:
                    if k in date_fields:
                        sheet.write(row, col, v, date)
                    elif k in money_fields:
                        sheet.write(row, col, v, money)
                    else:
                        sheet.write(row, col, v)
                    col += 1
            row += 1

        return sheet


    def get(self, request):
        workbook = xlsxwriter.Workbook('jpk_vat_new10.xlsx')
        worksheet1 = workbook.add_worksheet()
        worksheet2 = workbook.add_worksheet()

        # excel cell formatting
        bold = workbook.add_format({'bold': True})
        date = workbook.add_format({'num_format': 'dd/mm/yy'})
        money = workbook.add_format({'num_format': '#.00'})

        sale_keys = ['LpSprzedazy', 'NrKontrahenta', 'NazwaKontrahenta', 'AdresKontrahenta', 'DowodSprzedazy',
                     'DataWystawienia', 'DataSprzedazy', 'K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16', 'K_17',
                     'K_18', 'K_19', 'K_20', 'K_21', 'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29',
                     'K_30', 'K_31', 'K_32', 'K_33', 'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39', '_state', 'id']

        purchase_keys = ['LpZakupu', 'NrDostawcy', 'NazwaDostawcy', 'AdresDostawcy', 'DowodZakupu', 'DataZakupu', 'DataWplywu',
                         'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50', '_state', 'id']


        date_fields = ['DataWystawienia', 'DataSprzedazy', 'DataZakupu', 'DataWplywu']
        money_fields = ['K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16', 'K_17', 'K_18', 'K_19', 'K_20', 'K_21',
                        'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29', 'K_30', 'K_31', 'K_32', 'K_33',
                        'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39', 'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50']

        sale_headers = self.get_headers(sale_keys, SprzedazWiersz)
        purchase_headers = self.get_headers(purchase_keys, ZakupWiersz)

        self.worksheet_generate(sale_headers, worksheet1, sale_keys, SprzedazWiersz, bold, date_fields, date, money_fields, money)
        self.worksheet_generate(purchase_headers, worksheet2, purchase_keys, ZakupWiersz, bold, date_fields, date,
                                money_fields, money)

        workbook.close()

        return redirect('conversion_db')



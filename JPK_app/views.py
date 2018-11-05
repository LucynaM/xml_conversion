import os
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from .models import LoadedFile
from .forms import LoadedFileForm
from django.conf import settings

from datetime import datetime

import xlsxwriter

from .tags import Tags
from .process_xml_data import fast_iter, get_ns, get_headers, change_data


# Create your views here.

class ConvertXLMView(View):


    # filling excel sheet with xml parsed data
    def fill_sheet(self, headers, sheet, results, bold, date, money, numbers, strings):

        col = 0
        row = 1
        for header in headers:
            sheet.write(0, col, header, bold)
            if 'K_' in header:
                sheet.set_column(col, col, 10)
            else:
                sheet.set_column(col, col, len(header))
            col += 1

        for result in results:
            col = 0
            for header in headers:

                if header in result.keys() and result[header] != None:
                    if 'Data' in header:
                        sheet.write(row, col, datetime.strptime(result[header], '%Y-%m-%d'), date)
                    elif 'K_' in header or 'Kwota' in header or 'Bilans' in header or 'Saldo' in header or 'Obroty' in header\
                            or 'Wartosc' in header or 'Cena' in header:
                        sheet.write(row, col, float(result[header]), money)
                    elif 'Lp' in header:
                        sheet.write(row, col, row, numbers)
                    else:
                        sheet.write(row, col, result[header], strings)
                else:
                    sheet.write(row, col, None)
                col += 1
            row += 1

        return sheet

    # building excel worksheet
    def worksheets_generate(self, tags, workbook, file, func, ns, *args, **kwargs):
        for key, value in tags.items():

            worksheet = workbook.add_worksheet(name=key)

            if key == 'KontoZapisRestructured':
                results = fast_iter(file, ns + 'KontoZapis')
                headers = get_headers(value, results)
                headers.insert(2, 'KodKonta')
                results = change_data(results)

            else:
                results = fast_iter(file, ns + key)
                headers = get_headers(value, results)

            func(headers, worksheet, results, *args, **kwargs)


    # display upload form
    def get(self, request):

        form = LoadedFileForm()
        ctx = {'form': form}

        return render(request, 'conversion.html', ctx)


    # handle uploaded file
    def post(self, request):

        form = LoadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = LoadedFile.objects.create(**form.cleaned_data)


            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = "attachment; filename={}.xlsx".format(file.name[6:-4:])


            # basic excel settings
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})

            # excel cell formatting
            bold = workbook.add_format({'bold': True})
            date = workbook.add_format({'num_format': 'dd/mm/yy'})
            money = workbook.add_format({'num_format': '#,##0.00'})
            numbers = workbook.add_format({'num_format': '0'})
            strings = workbook.add_format({'num_format': '@'})

            date_fields = ['DataWystawienia', 'DataSprzedazy', 'DataZakupu', 'DataWplywu', 'DataOperacji', 'DataDowodu',
                           'DataKsiegowania', 'DataPZ', 'DataOtrzymaniaPZ', 'DataFaPZ', 'DataWZ', 'DataWydaniaWZ', 'DataFaWZ',
                           'DataRW', 'DataWydaniaRW', 'DataMM', 'DataWydaniaMM', 'DataOperacji', 'P_1', 'P_6', 'P_22A']

            money_fields = ['K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16', 'K_17', 'K_18', 'K_19', 'K_20',
                            'K_21', 'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29', 'K_30', 'K_31',
                            'K_32', 'K_33', 'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39', 'K_43', 'K_44', 'K_45',
                            'K_46', 'K_47', 'K_48', 'K_49', 'K_50', 'BilansOtwarciaWinien', 'BilansOtwarciaMa',
                            'ObrotyWinien', 'ObrotyMa', 'ObrotyWinienNarast', 'ObrotyMaNarast', 'SaldoWinien',
                            'SaldoMa', 'DziennikKwotaOperacji', 'KwotaWinien', 'KwotaMa', 'WartoscPZ', 'CenaJednPZ',
                            'WartoscPozycjiPZ', 'WartoscWZ', 'CenaJednWZ', 'WartoscPozycjiWZ', 'WartoscRW', 'CenaJednRW',
                            'WartoscPozycjiRW', 'WartoscMM', 'CenaJednMM', 'WartoscPozycjiMM', 'SaldoPoczatkowe',
                            'SaldoKoncowe', 'KwotaOperacji', 'SaldoOperacji', 'P_13_1', 'P_14_1', 'P_13_2', 'P_14_2',
                            'P_13_3', 'P_14_3', 'P_13_4', 'P_14_4', 'P_13_5', 'P_14_5', 'P_13_6', 'P_13_7', 'P_15', ]

            quantity_fileds = ['IloscPrzyjetaPZ', 'IloscWydanaWZ', 'IloscWydanaRW', 'IloscWydanaMM', ]

            ns = get_ns(file)
            obj = None
            for tag in Tags:
                if tag.ns == ns:
                    obj = tag
            tags = obj.tags


            self.worksheets_generate(tags, workbook, file, self.fill_sheet, ns, bold, date, money, numbers, strings)

            workbook.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form,}
        return render(request, 'conversion.html', ctx)

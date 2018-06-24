import os
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from .models import LoadedFile
from .forms import LoadedFileForm
from django.conf import settings

from datetime import datetime

import xlsxwriter
import lxml.etree as ET



# Create your views here.

class ConvertXLMView(View):

    # iterating through xml structure Based on Liza Daly's fast_iter
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    def fast_iter(self, file, process_func, tag, *args, **kwargs):

        context = ET.iterparse(file.path.url[1::], events=('end',), tag=tag)
        results = []

        for event, elem in context:
            process_func(elem, results)
            elem.clear()
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context
        return results


    # getting type of file (VAT, KR...) by reading the beginning of xml file in search of namespace tag
    def get_ns(self, file):

        ns = ""

        with open(file.path.url[1::], 'r') as f:
            start = f.read(200)
            if 'http://jpk.mf.gov.pl/wzor/2016/10/26/10261/' in start:
                ns = '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}'
            elif 'http://jpk.mf.gov.pl/wzor/2016/03/09/03091/' in start:
                ns = '{http://jpk.mf.gov.pl/wzor/2016/03/09/03091/}'

        f.close()
        return ns


    # processing xml elements to arrange them in key-value pairs (dictionary)
    def process_elem(self, elem, results):
        result = {}
        for child in elem.iterchildren():
            result[child.tag[child.tag.index('}')+1:]] = child.text
        results.append(result)


    # creating list of exel columns that are not empty
    def get_headers(self, keys, results):
        headers = []
        for el in keys:
            test_if_empty = len([True for result in results if el not in result.keys()])
            if test_if_empty != len(results):
                headers.append(el)
        return headers

    # change parsing result in order to get KodKonta instead of KodKontaWinien/KodKontaMa with values in a single row -generic
    def change_data_generic(self, result, required_elements, optional_elements):
        new_result = required_elements
        for el in optional_elements:
            if el in result.keys():
                new_result[el] = result[el]
        return new_result

    # change parsing result in order to get KodKonta instead of KodKontaWinien/KodKontaMa with values in a single row - application
    def change_data(self, results):
        new_results = []

        for result in results:
            debit_elements = {
                    'LpZapisu': result['LpZapisu'],
                    'NrZapisu': result['NrZapisu'],
                    'KodKonta': result['KodKontaWinien'],
                    'KwotaWinien': result['KwotaWinien'],
                    'KwotaMa': None,
                    'OpisZapisuMa': None,
                }
            credit_elements = {
                    'LpZapisu': result['LpZapisu'],
                    'NrZapisu': result['NrZapisu'],
                    'KodKonta': result['KodKontaMa'],
                    'KwotaWinien': None,
                    'OpisZapisuWinien': None,
                    'KwotaMa': result['KwotaMa'],
                }
            debit_optional_elements = ['KwotaWinienWaluta', 'KodWalutyWinien', 'OpisZapisuWinien']
            credit_optional_elements = ['KwotaMaWaluta', 'KodWalutyMa', 'OpisZapisuMa']

            if result['KodKontaWinien'] not in [None, '-'] and result['KodKontaMa'] not in [None, '-']:

                new_result = self.change_data_generic(result, debit_elements, debit_optional_elements)
                new_results.append(new_result)

                new_result = self.change_data_generic(result, credit_elements, credit_optional_elements)
                new_results.append(new_result)

            elif result['KodKontaWinien'] not in [None, '-']:

                new_result = self.change_data_generic(result, debit_elements, debit_optional_elements)
                new_results.append(new_result)

            elif result['KodKontaMa'] not in [None, '-']:

                new_result = self.change_data_generic(result, credit_elements, credit_optional_elements)
                new_results.append(new_result)

        return new_results

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
                results = self.fast_iter(file, self.process_elem, ns + 'KontoZapis')
                headers = self.get_headers(value, results)
                headers.insert(2, 'KodKonta')
                results = self.change_data(results)

            else:
                results = self.fast_iter(file, self.process_elem, ns + key)
                headers = self.get_headers(value, results)

            func(headers, worksheet, results, *args, **kwargs)


    # displaying upload form
    def get(self, request):

        form = LoadedFileForm()
        ctx = {'form': form}

        return render(request, 'conversion.html', ctx)


    # handling uploaded file
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


            ns = self.get_ns(file)

            # tags for JPK_VAT
            if ns == '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}':
                tags = {
                    'SprzedazWiersz': ['LpSprzedazy', 'NrKontrahenta', 'NazwaKontrahenta', 'AdresKontrahenta',
                                       'DowodSprzedazy', 'DataWystawienia', 'DataSprzedazy', 'K_10', 'K_11', 'K_12',
                                       'K_13', 'K_14', 'K_15', 'K_16', 'K_17', 'K_18', 'K_19', 'K_20', 'K_21', 'K_22',
                                       'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29', 'K_30', 'K_31', 'K_32',
                                       'K_33', 'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39'],
                    'ZakupWiersz': ['LpZakupu', 'NrDostawcy', 'NazwaDostawcy', 'AdresDostawcy', 'DowodZakupu',
                                    'DataZakupu', 'DataWplywu', 'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50'],
                        }

            # tags for JPK_KR
            elif ns == '{http://jpk.mf.gov.pl/wzor/2016/03/09/03091/}':
                tags = {
                    'ZOiS': ['KodKonta', 'OpisKonta', 'TypKonta', 'KodZespolu', 'OpisZespolu', 'KodKategorii', 'OpisKategorii',
                             'KodPodkategorii', 'OpisPodkategorii', 'BilansOtwarciaWinien', 'BilansOtwarciaMa',
                             'ObrotyWinien', 'ObrotyMa', 'ObrotyWinienNarast', 'ObrotyMaNarast', 'SaldoWinien', 'SaldoMa'],
                    'Dziennik': ['LpZapisuDziennika', 'NrZapisuDziennika', 'OpisDziennika', 'NrDowoduKsiegowego',
                                 'RodzajDowodu', 'DataOperacji', 'DataDowodu', 'DataKsiegowania', 'KodOperatora',
                                 'OpisOperacji', 'DziennikKwotaOperacji'],
                    'KontoZapis': ['LpZapisu', 'NrZapisu', 'KodKontaWinien', 'KwotaWinien', 'KwotaWinienWaluta',
                                   'KodWalutyWinien', 'OpisZapisuWinien', 'KodKontaMa', 'KwotaMa', 'KwotaMaWaluta',
                                   'KodWalutyMa', 'OpisZapisuMa'],
                    'KontoZapisRestructured': ['LpZapisu', 'NrZapisu', 'KwotaWinien', 'KwotaWinienWaluta',
                                              'KodWalutyWinien', 'OpisZapisuWinien', 'KwotaMa', 'KwotaMaWaluta',
                                              'KodWalutyMa', 'OpisZapisuMa'],
                }

            # tags for JPK_MAG
            elif ns == '{http://jpk.mf.gov.pl/wzor/2016/03/09/03093/}':
                tags = {
                    'PZWartosc': ['NumerPZ', 'DataPZ', 'WartoscPZ', 'DataOtrzymaniaPZ', 'Dostawca', 'NumerFaPZ', 'DataFaPZ'],
                    'PZWiersz': ['Numer2PZ', 'KodTowaruPZ', 'NazwaTowaruPZ', 'IloscPrzyjetaPZ', 'JednostkaMiaryPZ',
                                 'CenaJednPZ', 'WartoscPozycjiPZ'],
                    'WZWartosc': ['NumerWZ', 'DataWZ', 'WartoscWZ', 'DataWydaniaWZ', 'OdbiorcaWZ', 'NumerFaWZ', 'DataFaWZ'],
                    'WZWiersz': ['Numer2WZ', 'KodTowaruWZ', 'NazwaTowaruWZ', 'IloscWydanaWZ', 'JednostkaMiaryWZ',
                                 'CenaJednWZ', 'WartoscPozycjiWZ'],
                    'RWWartosc': ['NumerRW', 'DataRW', 'WartoscRW', 'DataWydaniaRW', 'SkadRW', 'DokadRW'],
                    'RWWiersz': ['Numer2RW', 'KodTowaruRW', 'NazwaTowaruRW', 'IloscWydanaRW', 'JednostkaMiaryRW',
                                 'CenaJednRW', 'WartoscPozycjiRW'],
                    'MMWartosc': ['NumerMM', 'DataMM', 'WartoscMM', 'DataWydaniaMM', 'SkadMM', 'DokadMM'],
                    'MMWiersz': ['Numer2MM', 'KodTowaruMM', 'NazwaTowaruMM', 'IloscWydanaMM', 'JednostkaMiaryMM',
                                 'CenaJednMM', 'WartoscPozycjiMM'],
                }

            # tags for JPK_WB
            elif ns == '{http://jpk.mf.gov.pl/wzor/2016/03/09/03092/}':
                tags = {
                    'Salda': ['SaldoPoczatkowe', 'SaldoKoncowe'],
                    'WyciagWiersz': ['NumerWiersza', 'DataOperacji', 'NazwaPodmiotu', 'OpisOperacji', 'KwotaOperacji',
                                     'SaldoOperacji']
                }

            # tags for JPK_FA
            elif ns == '{http://jpk.mf.gov.pl/wzor/2016/03/09/03095/}':
                tags = {
                    'Faktura': ['P_1', 'P_2A', 'P_3A', 'P_3B', 'P_3C', 'P_3D', 'P_4A', 'P_4B', 'P_5A', 'P_5B', 'P_6',
                                'P_13_1', 'P_14_1', 'P_13_2', 'P_14_2', 'P_13_3', 'P_14_3', 'P_13_4', 'P_14_4', 'P_13_5',
                                'P_14_5', 'P_13_6', 'P_13_7', 'P_15', 'P_16', 'P_17', 'P_18', 'P_19', 'P_19A', 'P_19B',
                                'P_19C', 'P_20', 'P_20A', 'P_20B', 'P_21', 'P_21A', 'P_21B', 'P_21C', 'P_22A', 'P_22B',
                                'P_22C', 'P_23', 'P_106E_2', 'P_106E_3', 'P_106E_3A']

                }



            self.worksheets_generate(tags, workbook, file, self.fill_sheet, ns, bold, date, money, numbers, strings)

            workbook.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form,}
        return render(request, 'conversion.html', ctx)

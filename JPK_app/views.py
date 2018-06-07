import os
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SprzedazWiersz, ZakupWiersz, LoadedFile, Dziennik, KontoZapis
from .forms import LoadedFileForm, RegistrationForm, LogInForm
from django.contrib.auth import login, logout, authenticate
from django.conf import settings

import xlsxwriter
import lxml.etree as ET



# Create your views here.

class ConvertXLMView(LoginRequiredMixin, View):

    # building element tag name
    def fixtag(self, ns, tag, nsmap):
        return '{' + nsmap[ns] + '}' + tag


    # iterating through xml structure Based on Liza Daly's fast_iter
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    def fast_iter(self, file, process_func, tag, *args, **kwargs):

        nsmap = {}
        context = ET.iterparse(file.path.url[1::], events=('end', 'start-ns',), tag=tag)
        results = []

        for event, elem in context:
            if event == 'start-ns':
                ns, url = elem
                nsmap[ns] = url
            if event == 'end':
                process_func(elem, results, *args, **kwargs)
                elem.clear()
                for ancestor in elem.xpath('ancestor-or-self::*'):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]
        del context
        return results


    # processing xml elements
    def process_elem(self, elem, results, *args, **kwargs):
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

    # building excel sheet
    def worksheet_generate(self, headers, sheet, results, bold, date, money, numbers, strings):

        col = 0
        row = 1
        for header in headers:
            sheet.write(0, col, header, bold)
            col += 1

        for result in results:
            col = 0
            for header in headers:
                if header not in result.keys():
                    result[header] = None
                if 'Data' in header:
                    sheet.write(row, col, result[header], date)
                elif 'K_' in header or 'Kwota' in header or 'Bilans' in header or 'Saldo' in header or 'Obroty' in header:
                    sheet.write(row, col, result[header], money)
                elif 'Lp' in header:
                    sheet.write(row, col, result[header], numbers)
                else:
                    sheet.write(row, col, result[header], strings)
                col += 1
            row += 1
        return sheet

    def worksheets_generate(self, tags, workbook, file, ns, func,  *args, **kwargs):
        for key, value in tags.items():
            worksheet = workbook.add_worksheet()
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

        user = User.objects.get(pk=request.user.id)
        form = LoadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = LoadedFile.objects.create(user=user, **form.cleaned_data)

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = "attachment; filename={}.xlsx".format(file.get_type_display())


            # basic excel settings
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})

            # excel cell formatting
            bold = workbook.add_format({'bold': True})
            date = workbook.add_format({'num_format': 'dd/mm/yy'})
            money = workbook.add_format({'num_format': '#.00'})
            numbers = workbook.add_format({'num_format': '0'})
            strings = workbook.add_format({'num_format': '@'})


            if file.get_type_display() == 'VAT':
                ns = '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}'
                tags = {
                    'SprzedazWiersz':
                            ['LpSprzedazy', 'NrKontrahenta', 'NazwaKontrahenta', 'AdresKontrahenta', 'DowodSprzedazy',
                             'DataWystawienia', 'DataSprzedazy', 'K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16',
                             'K_17', 'K_18', 'K_19', 'K_20', 'K_21', 'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27',
                             'K_28', 'K_29', 'K_30', 'K_31', 'K_32', 'K_33', 'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39'],
                   'ZakupWiersz':
                           ['LpZakupu', 'NrDostawcy', 'NazwaDostawcy', 'AdresDostawcy', 'DowodZakupu', 'DataZakupu',
                            'DataWplywu', 'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50'],
                        }

                self.worksheets_generate(tags, workbook, file, ns, self.worksheet_generate, bold, date, money, numbers,
                                         strings)


            elif file.get_type_display() == 'KR':
                ns = '{http://jpk.mf.gov.pl/wzor/2016/03/09/03091/}'
                tags = {
                    'ZOiS': ['KodKonta', 'OpisKonta', 'TypKonta', 'KodZespolu', 'OpisZespolu', 'KodKategorii', 'OpisKategorii',
                             'KodPodkategorii', 'OpisPodkategorii', 'BilansOtwarciaWinien', 'BilansOtwarciaMa',
                             'ObrotyWinien', 'ObrotyMa', 'ObrotyWinienNarast', 'ObrotyMaNarast', 'SaldoWinien', 'SaldoMa'],
                    'Dziennik': ['LpZapisuDziennika', 'NrZapisuDziennika', 'OpisDziennika', 'NrDowoduKsiegowego',
                                 'RodzajDowodu', 'DataOperacji', 'DataDowodu', 'DataKsiegowania', 'KodOperatora',
                                 'OpisOperacji', 'DziennikKwotaOperacji'],
                    'KontoZapis': ['LpZapisu', 'NrZapisu', 'KodKontaWinien', 'KwotaWinien', 'KwotaWinienWaluta',
                                   'KodWalutyWinien', 'OpisZapisuWinien', 'KodKontaMa', 'KwotaMa', 'KwotaMaWaluta',
                                   'KodWalutyMa', 'OpisZapisuMa']
                }

                self.worksheets_generate(tags, workbook, file, ns, self.worksheet_generate, bold, date, money, numbers,
                                         strings)

            workbook.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form,}
        return render(request, 'conversion.html', ctx)



class Registration(View):
    """Registration page"""
    def get(self, request):
        form = RegistrationForm()
        ctx = {
            'form': form
        }
        return render(request, 'registration.html', ctx)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('password2')
            user = User.objects.create_user(username=form.cleaned_data['email'], **form.cleaned_data)
            login(request, user)
            return redirect('conversion_db')
        ctx = {
            'form': form,
        }
        return render(request, 'registration.html', ctx)


class LogInView(View):
    def get(self, request):
        form = LogInForm()
        ctx = {
            'form': form,
        }
        return render(request, 'login.html', ctx)

    def post(self, request):
        form = LogInForm(request.POST)
        msg = ""
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('conversion_db')
            else:
                msg = "Błędny użytkownik lub hasło"
        ctx = {
            'msg': msg,
            'form': form,
        }
        return render(request, 'login.html', ctx)


def logout_user(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SprzedazWiersz, ZakupWiersz, LoadedFile
from .forms import LoadedFileForm, RegistrationForm, LogInForm
from django.contrib.auth import login, logout, authenticate

import xml.etree.ElementTree as etree
import xlsxwriter


# Create your views here.


class ConvertToDBView(LoginRequiredMixin, View):

    def get_data(self, file, search_param, model):

        tree = etree.parse(file.path.url[1::])
        root = tree.getroot()
        container = {}
        for row in root.findall(search_param):
            for element in row:
                container[element.tag[element.tag.index('}')+1:]] = element.text
            model.objects.create(document=file, **container)
            container.clear()

    def get(self, request):
        form = LoadedFileForm()
        ctx = {'form': form}
        return render(request, 'sprzedaz.html', ctx)

    def post(self, request):
        user = User.objects.get(pk=request.user.id)
        form = LoadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = LoadedFile.objects.create(user=user, **form.cleaned_data)

            self.get_data(file, '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}SprzedazWiersz', SprzedazWiersz)
            self.get_data(file, '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}ZakupWiersz', ZakupWiersz)

            return redirect('export')

        ctx = {
            'form': form,
        }
        return redirect(request, 'sprzedaz.html', ctx)


class ExportToExcel(LoginRequiredMixin, View):

    def get_headers(self, obj_keys, query_set):
        container = []
        for el in obj_keys:
            if el not in ['_state', 'id', 'document_id']:
                test_if_empty = len([True for obj in query_set.objects.all() if getattr(obj, el) == None])
                if test_if_empty != query_set.objects.count():
                    container.append(el)
        return container

    def worksheet_generate(self, headers, sheet, keys, query_set, bold, date_fields, date, money_fields, money, num_fields, numbers, strings):
        col = 0
        row = 1
        for el in headers:
            if col in range(1, 5):
                sheet.set_column(col, col, 20)
            sheet.write(0, col, el, bold)
            col += 1

        for el in query_set.objects.all():
            col = 0
            for header in headers:
                if header in date_fields:
                    sheet.write(row, col, getattr(el, header), date)
                elif header in money_fields:
                    sheet.write(row, col, getattr(el, header), money)
                elif header in num_fields:
                    sheet.write(row, col, getattr(el, header), numbers)
                else:
                    sheet.write(row, col, getattr(el, header), strings)
                col += 1
            row += 1

        return sheet


    def get(self, request):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "attachment; filename=test.xlsx"

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet1 = workbook.add_worksheet()
        worksheet2 = workbook.add_worksheet()

        # excel cell formatting
        bold = workbook.add_format({'bold': True})
        date = workbook.add_format({'num_format': 'dd/mm/yy'})
        money = workbook.add_format({'num_format': '#.00'})
        numbers = workbook.add_format({'num_format': '0'})
        strings = workbook.add_format({'num_format': '@'})

        sale_keys = ['LpSprzedazy', 'NrKontrahenta', 'NazwaKontrahenta', 'AdresKontrahenta', 'DowodSprzedazy',
                     'DataWystawienia', 'DataSprzedazy', 'K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16', 'K_17',
                     'K_18', 'K_19', 'K_20', 'K_21', 'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29',
                     'K_30', 'K_31', 'K_32', 'K_33', 'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39', '_state', 'id', 'document_id']

        purchase_keys = ['LpZakupu', 'NrDostawcy', 'NazwaDostawcy', 'AdresDostawcy', 'DowodZakupu', 'DataZakupu', 'DataWplywu',
                         'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50', '_state', 'id', 'document_id']

        num_fields = ['LpSprzedazy', 'LpZakupu']
        date_fields = ['DataWystawienia', 'DataSprzedazy', 'DataZakupu', 'DataWplywu']
        money_fields = ['K_10', 'K_11', 'K_12', 'K_13', 'K_14', 'K_15', 'K_16', 'K_17', 'K_18', 'K_19', 'K_20', 'K_21',
                        'K_22', 'K_23', 'K_24', 'K_25', 'K_26', 'K_27', 'K_28', 'K_29', 'K_30', 'K_31', 'K_32', 'K_33',
                        'K_34', 'K_35', 'K_36', 'K_37', 'K_38', 'K_39', 'K_43', 'K_44', 'K_45', 'K_46', 'K_47', 'K_48', 'K_49', 'K_50']

        sale_headers = self.get_headers(sale_keys, SprzedazWiersz)
        purchase_headers = self.get_headers(purchase_keys, ZakupWiersz)

        self.worksheet_generate(sale_headers, worksheet1, sale_keys, SprzedazWiersz, bold, date_fields, date, money_fields, money, num_fields, numbers, strings)
        self.worksheet_generate(purchase_headers, worksheet2, purchase_keys, ZakupWiersz, bold, date_fields, date,
                                money_fields, money, num_fields, numbers, strings)

        workbook.close()
        return response




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
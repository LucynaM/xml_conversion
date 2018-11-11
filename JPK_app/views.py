import os
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from .models import LoadedFile, JPKFile, JPKTag, JPKTable
from .forms import LoadedFileForm, JPKFileForm, JPKTableForm, JPKTagForm
from django.conf import settings

import xlsxwriter

from .process_xml_data import get_ns
from .prepare_tags_scheme import prepare_tags_scheme
from .build_excel_file import worksheets_generate
import zipfile

# Create your views here.

class ConvertXLMView(View):

    # display upload form
    def get(self, request):

        form = LoadedFileForm()
        ctx = {'form': form}

        return render(request, 'JPK_app/conversion.html', ctx)


    # handle uploaded file
    def post(self, request):

        form = LoadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = LoadedFile.objects.create(**form.cleaned_data)

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = "attachment; filename={}.xlsx".format(file.name[6:-4:])

            # basic excel settings
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})

            # define type of xml file by getting its namespace
            ns = get_ns(file)

            # get tags of xml file based on its namespace
            obj = prepare_tags_scheme(ns)

            worksheets_generate(obj, workbook, file, ns)

            workbook.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form,}
        return render(request, 'JPK_app/conversion.html', ctx)


class JPKFileCreate(View):
    """create file"""
    def get(self, request):
        form = JPKFileForm()
        ctx = {
            'form': form,
        }
        return render(request, 'JPK_app/jpkfile_form.html', ctx)

    def post(self, request):
        form = JPKFileForm(request.POST)
        if form.is_valid():
            file = form.save()
            return redirect('file_show', pk=file.pk)
        ctx = {
            'form': form,
        }
        return render(request, 'JPK_app/jpkfile_form.html', ctx)


class JPKFileShow(View):
    """create tables in a file"""
    def get(self, request, pk):
        file = JPKFile.objects.get(pk=pk)
        form = JPKTableForm()
        tables = file.tables.all()
        ctx = {
            'file': file,
            'form': form,
            'tables': tables,
        }
        return render(request, 'JPK_app/jpkfile_show.html', ctx)

    def post(self, request, pk):
        file = JPKFile.objects.get(pk=pk)
        form = JPKTableForm(request.POST)

        if form.is_valid():
            table = JPKTable.objects.create(file=file, **form.cleaned_data)
            return redirect('table_show', pk=table.pk)

        tables = file.tables.all()
        ctx = {
            'file': file,
            'form': form,
            'tables': tables,
        }
        return render(request, 'JPK_app/jpkfile_show.html', ctx)


class JPKTableShow(View):
    """create tags in a table"""
    def get(self, request, pk):
        table = JPKTable.objects.get(pk=pk)
        file = JPKFile.objects.get(pk=table.file.pk)
        tags = table.tags.all()
        form = JPKTagForm()
        ctx = {
            'table': table,
            'file': file,
            'form': form,
            'tags': tags,
        }
        return render(request, 'JPK_app/jpktable_show.html', ctx)

    def post(self, request, pk):
        table = JPKTable.objects.get(pk=pk)
        file = JPKFile.objects.get(pk=table.file.pk)
        form = JPKTagForm(request.POST)

        if form.is_valid():
            JPKTag.objects.create(table=table, **form.cleaned_data)
            form = JPKTagForm()

        tags = table.tags.all()
        ctx = {
            'table': table,
            'file': file,
            'form': form,
            'tags': tags,
        }
        return render(request, 'JPK_app/jpktable_show.html', ctx)


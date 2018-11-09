import os
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from .models import LoadedFile
from .forms import LoadedFileForm
from django.conf import settings

import xlsxwriter

from .tags import Tags
from .process_xml_data import get_ns
from .process_xml_data_TEST import get_ns_TEST
from .build_excel_file import worksheets_generate
from .build_excel_file_TEST import worksheets_generate_TEST

import zipfile
import tarfile

# Create your views here.

class ConvertXLMView(View):

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

            # define type of xml file by getting its namespace
            ns = get_ns(file)
            # get tags of xml file based on namespace
            obj = None
            for tag in Tags:
                if tag.ns == ns:
                    obj = tag

            worksheets_generate(obj, workbook, file, ns)

            workbook.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form,}
        return render(request, 'conversion.html', ctx)


class TestView(View):
    def get(self, request):
        form = LoadedFileForm()
        ctx = {'form': form}
        return render(request, 'test_file.html', ctx)

        # handle uploaded file
    def post(self, request):

        form = LoadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = LoadedFile.objects.create(**form.cleaned_data)



            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = "attachment; filename={}.xlsx".format(file.name[6:-4:])

            # basic excel settings
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})

            with zipfile.ZipFile(file.path) as zip_file:
                names = zip_file.namelist()
                for name in names:
                    if '.xml' in name or '.XML' in name:
                        my_name = name
                elem = zip_file.extract(my_name)

                # define type of xml file by getting its namespace
                ns = get_ns_TEST(elem)
                # get tags of xml file based on namespace
                obj = None
                for tag in Tags:
                    if tag.ns == ns:
                        obj = tag

                worksheets_generate_TEST(obj, workbook, elem, ns)

                workbook.close()
                zip_file.close()

            # removing loaded file from db and from media folder
            file.delete()
            os.remove(os.path.join(settings.MEDIA_ROOT, file.name))

            return response

        form = LoadedFileForm()
        ctx = {'form': form, }
        return render(request, 'conversion.html', ctx)



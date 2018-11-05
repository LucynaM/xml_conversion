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
from .process_xml_data import get_ns
from .build_excel_file import worksheets_generate


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

            ns = get_ns(file)
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

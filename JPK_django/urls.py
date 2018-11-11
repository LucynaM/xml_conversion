"""JPK_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from JPK_app.views import ConvertXLMView, JPKFileCreate, JPKFileShow, JPKTableShow, JPKFileList, JPKFileEdit, JPKTableEdit, JPKTagEdit

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^conversion_db/$', ConvertXLMView.as_view(), name='conversion_db'),
    url(r'^file_create/$', JPKFileCreate.as_view(), name='file_create'),
    url(r'^file_show/(?P<pk>(\d)+)/$', JPKFileShow.as_view(), name='file_show'),
    url(r'^table_show/(?P<pk>(\d)+)/$', JPKTableShow.as_view(), name='table_show'),
    url(r'^file_list/$',JPKFileList.as_view(), name='file_list'),
    url(r'^file_edit/(?P<pk>(\d)+)/$', JPKFileEdit.as_view(), name='file_edit'),
    url(r'^table_edit/(?P<pk>(\d)+)/$', JPKTableEdit.as_view(), name='table_edit'),
    url(r'^tag_edit/(?P<pk>(\d)+)/$', JPKTagEdit.as_view(), name='tag_edit'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

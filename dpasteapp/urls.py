from .views import *
from django.urls import path


app_name = "dpasteapp"

urlpatterns = [
    path(r'', DpasteController.as_view(),name = "dpaste_form"),
    path(r'about',aboutDpaste,name = "dpaste_about"),
    path(r'history', DpasteListView.as_view(),name = "dpastelist"),
    path(r'<str:link>', DpasteView.as_view(),name = "dpaste_view"),
]
from django.urls import path
from .views import *

urlpatterns = [
    path('', upload_home, name='upload_home'),        # 👈 LANDING PAGE (UPLOAD)
    path('records/', record_list, name='record_list'),# 👈 VIEW CRUD TABLE
    path('form/', record_form, name='record_create'),
    path('form/<int:pk>/', record_form, name='record_edit'),
    path('delete/<int:pk>/', record_delete, name='record_delete'),
    path('upload/bulk/', bulk_upload, name='bulk_upload'),
    path('inline-edit/<int:pk>/<str:field>/', inline_edit, name='inline_edit'),  # 👈 AJAX EDIT
]

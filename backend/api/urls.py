from django.urls import path
from .views import UploadCSVView, HistoryView, GeneratePDFView, CustomAuthToken

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload-csv'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:dataset_id>/', GeneratePDFView.as_view(), name='generate-pdf'),
    path('login/', CustomAuthToken.as_view(), name='login'),
]

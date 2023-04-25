from django.urls import path
from .views import create_crop

urlpatterns = [
  path('create_crop/', create_crop, name='create_crop'),
]

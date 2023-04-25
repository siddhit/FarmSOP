from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
  path('', RedirectView.as_view(url='/create_crop/', permanent=True)),
  path('', include('farmsop_app.urls')),
]

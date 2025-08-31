# sipmi_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sipmi_core.urls')), # Include your app's URLs
    # Add auth URLs if using custom password management
    # path('accounts/', include('django.contrib.auth.urls')),
]

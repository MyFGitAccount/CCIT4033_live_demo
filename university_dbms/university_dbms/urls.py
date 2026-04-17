from django.contrib import admin
from django.urls import path, include
from university_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('university_app.urls')),
]

from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('library.urls')),
    path("auth/", include("authentication.urls")),
    path('dashboard1/', include('dashboard1.urls')),
    path('dashboard2/', include('dashboard2.urls')),
]



    


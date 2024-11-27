from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

media_and_static_url = [
    path('media/<path:path>', serve, kwargs={'document_root': settings.MEDIA_ROOT}),
    path('static/<path:path>', serve, kwargs={'document_root': settings.STATIC_ROOT}),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('users/', include('users.urls')),
    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')),
    path('appointment/', include('appointment.urls')),
    path('book/', include('medicalBook.urls')),
    path('chat/', include('chat.urls')),
]

urlpatterns += media_and_static_url


from django.contrib import admin
from django.urls import path, include
from .views import home
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('', include('accounts.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

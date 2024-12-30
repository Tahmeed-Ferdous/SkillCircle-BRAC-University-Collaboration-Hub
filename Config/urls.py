from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from authy.views import UserProfile, follow

urlpatterns = [
    path('admin/', admin.site.urls),
    path('post/', include('post.urls')),
    path('', include('authy.urls')),
    path('explore/', include('explore.urls', namespace='explore')),
    path('direct/', include('direct.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('settings/', include('setting.urls', namespace='setting')),
    path('<username>/', UserProfile, name='profile'),
    path('<username>/saved', UserProfile, name='profilefavorites'),
    path('<username>/follow/<option>', follow, name='follow'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

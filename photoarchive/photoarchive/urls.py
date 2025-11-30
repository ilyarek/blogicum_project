from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from archive import views  # импортируем представления из приложения archive

urlpatterns = [
    # Кастомные админ-маршруты ДО стандартной админки
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/dashboard/document/<int:pk>/toggle/', views.toggle_document_status, name='toggle_document_status'),
    path('admin/dashboard/document/<int:pk>/delete/', views.delete_document, name='delete_document'),
    
    # Стандартная админка Django
    path('admin/', admin.site.urls),
    
    # Остальные маршруты приложения archive
    path('', include('archive.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
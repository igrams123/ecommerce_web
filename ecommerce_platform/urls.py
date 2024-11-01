from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface URL
    path('', include('shop.urls')),  # Include shop URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login view
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Logout view
    path('register/', views.register, name='register'),  # Register view
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

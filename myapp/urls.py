from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True, next_page='home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('table/<int:table_number>/menu/', views.menu, name='menu'),
    path('table/<int:table_num>/order/submit/', views.submit_order_view, name='submit_order'),
    path('kds/', views.kds_view, name='kds'),
    path('kds/update/<int:order_id>/', views.update_order_status_view, name='update_order'),
]

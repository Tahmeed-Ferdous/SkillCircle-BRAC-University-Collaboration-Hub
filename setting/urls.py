from django.urls import path
from . import views

app_name = 'setting'

urlpatterns = [
    path('', views.settings_page, name='settings_page'),
    path('change_password/', views.change_password, name='change_password'),
    path('privacy_settings/', views.privacy_settings, name='privacy_settings'),
    path('notification_settings/', views.notification_settings, name='notification_settings'),
    path('blocked_users/', views.blocked_users, name='blocked_users'),
    path('linked_accounts/', views.linked_accounts, name='linked_accounts'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('update_contact_info/', views.update_contact_info, name='update_contact_info'),
]

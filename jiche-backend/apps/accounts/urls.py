from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('auth/login/', views.PasswordLoginView.as_view(), name='auth-password-login'),
    path('auth/wx-mini/login/', views.WxMiniLoginView.as_view(), name='auth-wx-mini-login'),
    path('auth/login-ticket/', views.CreateLoginTicketView.as_view(), name='auth-login-ticket-create'),
    path('auth/login-ticket/<str:ticket_id>/', views.PollLoginTicketView.as_view(), name='auth-login-ticket-poll'),
    path(
        'auth/login-ticket/<str:ticket_id>/confirm/',
        views.ConfirmLoginTicketView.as_view(),
        name='auth-login-ticket-confirm',
    ),
    path(
        'auth/login-ticket/<str:ticket_id>/simulate/',
        views.SimulateScanLoginView.as_view(),
        name='auth-login-ticket-simulate',
    ),
    # PRD 别名
    path('auth/wx-scan/ticket/', views.CreateLoginTicketView.as_view(), name='auth-wx-scan-ticket'),
    path('auth/wx-scan/poll/<str:ticket_id>/', views.PollLoginTicketView.as_view(), name='auth-wx-scan-poll'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/dev/login/', views.DevLoginView.as_view(), name='auth-dev-login'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/grant-staff/', views.GrantStaffView.as_view(), name='admin-grant-staff'),
    path('admin/users/<int:user_id>/revoke-staff/', views.RevokeStaffView.as_view(), name='admin-revoke-staff'),
]

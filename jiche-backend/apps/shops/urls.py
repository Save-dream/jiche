from django.urls import path

from apps.shops import views

urlpatterns = [
    path('uploads/image/', views.ImageUploadView.as_view(), name='upload-image'),
    path('applications/', views.SubmitApplicationView.as_view(), name='applications-submit'),
    path('applications/my/', views.MyApplicationView.as_view(), name='applications-my'),
    path('admin/applications/', views.AdminApplicationListView.as_view(), name='admin-applications'),
    path(
        'admin/applications/<int:application_id>/audit/',
        views.AdminApplicationAuditView.as_view(),
        name='admin-application-audit',
    ),
    path('shops/<int:shop_id>/', views.ShopDetailView.as_view(), name='shop-detail'),
    path('shop/profile/', views.ShopProfileView.as_view(), name='shop-profile'),
    path('admin/shops/', views.AdminShopListView.as_view(), name='admin-shops'),
    path('admin/shops/<int:shop_id>/ban/', views.AdminShopBanView.as_view(), name='admin-shop-ban'),
    path('admin/shops/<int:shop_id>/unban/', views.AdminShopUnbanView.as_view(), name='admin-shop-unban'),
    path('visits/', views.VisitView.as_view(), name='visits'),
    path('shop/stats/', views.ShopStatsView.as_view(), name='shop-stats'),
    path('admin/stats/', views.AdminStatsView.as_view(), name='admin-stats'),
]

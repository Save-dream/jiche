from django.urls import path

from apps.bikes import views

urlpatterns = [
    path('bikes/<int:bike_id>/', views.BikeDetailView.as_view(), name='bike-detail'),
    path('s/<str:short_code>/', views.ResolveShareLinkView.as_view(), name='share-resolve'),
    path('shop/bikes/', views.ShopBikeListCreateView.as_view(), name='shop-bikes'),
    path('shop/bikes/<int:bike_id>/', views.ShopBikeDetailView.as_view(), name='shop-bike-detail'),
    path('shop/bikes/<int:bike_id>/off-shelf/', views.ShopBikeOffShelfView.as_view(), name='shop-bike-off-shelf'),
    path('shop/bikes/<int:bike_id>/on-shelf/', views.ShopBikeOnShelfView.as_view(), name='shop-bike-on-shelf'),
    path('shop/bikes/<int:bike_id>/mark-sold/', views.ShopBikeMarkSoldView.as_view(), name='shop-bike-mark-sold'),
    path('shop/bikes/<int:bike_id>/share-link/', views.ShopBikeShareLinkView.as_view(), name='shop-bike-share-link'),
    path('admin/bikes/', views.AdminBikeListView.as_view(), name='admin-bikes'),
    path(
        'admin/bikes/<int:bike_id>/force-off-shelf/',
        views.AdminBikeForceOffShelfView.as_view(),
        name='admin-bike-force-off',
    ),
    path(
        'admin/bikes/<int:bike_id>/restore/',
        views.AdminBikeRestoreView.as_view(),
        name='admin-bike-restore',
    ),
    path(
        'admin/bikes/<int:bike_id>/',
        views.AdminBikeDeleteView.as_view(),
        name='admin-bike-delete',
    ),
]

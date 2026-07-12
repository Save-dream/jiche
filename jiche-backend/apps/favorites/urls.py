from django.urls import path

from apps.favorites import views

urlpatterns = [
    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorites'),
    path('favorites/<int:bike_id>/', views.FavoriteDeleteView.as_view(), name='favorite-delete'),
]

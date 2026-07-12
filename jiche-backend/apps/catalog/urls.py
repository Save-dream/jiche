from django.urls import path

from apps.catalog import views

urlpatterns = [
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('brands/<int:brand_id>/models/', views.BrandModelsView.as_view(), name='brand-models'),
]

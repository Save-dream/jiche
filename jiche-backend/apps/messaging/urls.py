from django.urls import path

from apps.messaging import views

urlpatterns = [
    path('message-threads/', views.MessageThreadListCreateView.as_view(), name='message-threads'),
    path('message-threads/<int:thread_id>/', views.MessageThreadDetailView.as_view(), name='message-thread-detail'),
    path(
        'message-threads/<int:thread_id>/messages/',
        views.MessageThreadSendView.as_view(),
        name='message-thread-send',
    ),
    path(
        'message-threads/<int:thread_id>/read/',
        views.MessageThreadReadView.as_view(),
        name='message-thread-read',
    ),
    path('messages/unread-count/', views.UnreadCountView.as_view(), name='messages-unread-count'),
    path('shop/message-threads/', views.ShopMessageThreadListView.as_view(), name='shop-message-threads'),
    path('admin/message-threads/', views.AdminMessageThreadListView.as_view(), name='admin-message-threads'),
]

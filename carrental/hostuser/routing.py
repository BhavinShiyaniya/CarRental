from django.urls import path, re_path
from hostuser import consumers

# websocket_urlpatterns = [
#     path('hostuser/ws/notification/', consumers.NotificationConsumer.as_asgi()),
#     # re_path(r'ws/notification/$', consumers.NotificationConsumer.as_asgi()),
# ]


websocket_urlpatterns = [
    path('ws/notification/', consumers.NotificationConsumer.as_asgi()),
]
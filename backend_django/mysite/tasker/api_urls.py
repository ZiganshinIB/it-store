from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .api_views import (ApprovalRouteViewSet, RequestTemplateViewSet, TaskTemplateViewSet,
                        CreateRequestView, ListRequestView, DetailRequestView,
                        CanselRequestView, AppointRequestView)


app_name = "api_tasker"

router = SimpleRouter()
router.register('approval_route', ApprovalRouteViewSet)
router.register('request_template', RequestTemplateViewSet)
router.register('task_template', TaskTemplateViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('request/', CreateRequestView.as_view(), name='create-request'),
    path('request/', ListRequestView.as_view(), name='list-request'),
    path('request/<int:pk>/', DetailRequestView.as_view(), name='detail-request'),
    path('request/<int:pk>/cansel/', CanselRequestView.as_view(), name='cansel-request'),
    path('request/<int:pk>/appoint/', AppointRequestView.as_view(), name='appoint-request'),
    # path('request/<int:pk>/accept/', RequestViewSet.as_view({'get': 'accept'}), name='accept-request'),
    # path('request/<int:pk>/appoint/', RequestViewSet.as_view({'put': 'appoint'}), name='appoint-request'),
    # path('request/<int:pk>/hire/', RequestViewSet.as_view({'get': 'hire'}), name='hire-request'),
    # path('request/<int:pk>/cansel/', RequestViewSet.as_view({'get': 'cansel'}), name='cansel-request'),
    # path('request/<int:pk>/chk/', RequestViewSet.as_view({'get': 'chk'}), name='chk-request'),
    # path('request/<int:pk>/reject/', RequestViewSet.as_view({'get': 'reject'}), name='reject-request'),

]
from django.conf.urls import url

from rest_framework.routers import SimpleRouter

from .views import OrderViewSet, OrganizationViewSet
from .utils import CustomAuthToken

router = SimpleRouter()
router.register('organizations', OrganizationViewSet)
router.register('orders', OrderViewSet, basename='order')


urlpatterns = [
    # url(r'order/', OrderListCreateView.as_view(), name='create_order'),
    url(r'login/', CustomAuthToken.as_view()),
    # url(r'get_all_orders/', OrderList.as_view()),
]

urlpatterns += router.urls

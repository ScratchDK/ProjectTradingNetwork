from rest_framework import routers

from network import views

app_name = "network"

router = routers.DefaultRouter()

router.register(r"factories", views.FactoryViewSet)
router.register(r"retail-networks", views.RetailNetworkViewSet)
router.register(r"entrepreneurs", views.IndividualEntrepreneurViewSet)
router.register(r"products", views.ProductViewSet)

urlpatterns = [] + router.urls

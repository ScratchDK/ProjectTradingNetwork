from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Factory, IndividualEntrepreneur, Product, RetailNetwork
from .paginators import MyPagination
from .permissions import IsActiveEmployee
from .serializers import (FactorySerializer, IndividualEntrepreneurSerializer,
                          ProductSerializer, RetailNetworkSerializer)


class BaseNetworkViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country"]
    permission_classes = [IsActiveEmployee]
    pagination_class = MyPagination


class FactoryViewSet(BaseNetworkViewSet):
    queryset = Factory.objects.all()
    serializer_class = FactorySerializer


class RetailNetworkViewSet(BaseNetworkViewSet):
    queryset = RetailNetwork.objects.all()
    serializer_class = RetailNetworkSerializer


class IndividualEntrepreneurViewSet(BaseNetworkViewSet):
    queryset = IndividualEntrepreneur.objects.all()
    serializer_class = IndividualEntrepreneurSerializer


class ProductViewSet(BaseNetworkViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["name", "model"]

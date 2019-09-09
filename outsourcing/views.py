from datetime import datetime

from rest_framework import generics, views, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .serializers import OrderSerializer, OrganizationSerializer, OrderRequestSerializer, AcceptOrderRequestSerializer, \
    TagSerializer, ReviewSerializer, TokenSerializer
from .permissions import IsOrderCreator, NotOrderCreator, IsOrganizationCreator, NotOrganizationCreator
from .models import Order, Organization, OrderRequest, Tag, Review
from .models import STATUS_NOT_ACCEPTED, STATUS_ACCEPTED, STATUS_COMPLETED
from .tokens import account_activation_token


class OrderViewSet(viewsets.ModelViewSet):
    # viewset for organization to work with orders
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()  # .filter(customer=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'get_order_requests', 'accept_order_request',
                           'add_tag', 'remove_performer', 'complete order']:
            permission_classes = [IsOrderCreator, IsAuthenticated]
        elif self.action in ['list', 'retrieve', 'get_tags']:
            permission_classes = []
        elif self.action == 'apply_for_order':
            permission_classes = [IsAuthenticated, NotOrderCreator]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=True,
            methods=['post'],
            serializer_class=OrderRequestSerializer)
    def apply_for_order(self, request, pk):
        order = self.get_object()
        if order.status == STATUS_NOT_ACCEPTED:
            ser_class = self.get_serializer_class()
            data = {
                'order': order,
                'performer': request.user,
                'comment': request.data['comment']
            }

            ser = ser_class(data=data)
            if ser.is_valid():
                OrderRequest.objects.create(**data)
                return Response({'status': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response(ser.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'can\'t apply for accepted/completed order'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['get'],
            serializer_class=OrderRequestSerializer)
    def get_order_requests(self, request, pk):
        order = self.get_object()
        queryset = order.orderrequest_set.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            serializer_class=AcceptOrderRequestSerializer)
    def accept_order_request(self, request, pk):
        order = self.get_object()
        order_request_id = request.data['order_request_id']
        if order.orderrequest_set.filter(pk=order_request_id):
            order.status = STATUS_ACCEPTED
            order.save(update_fields=['status'])
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'order request with this id not found'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post'])
    def complete_order(self, request, pk):
        order = self.get_object()
        order.status = STATUS_COMPLETED
        order.date_completed = datetime.now()
        order.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['post'])
    def remove_performer(self, request, pk):
        order = self.get_object()
        order.performer = None
        order.status = STATUS_NOT_ACCEPTED
        order.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'get_requested_orders']:
            permission_classes = [IsAuthenticated, IsOrganizationCreator]
        elif self.action in ['make_review', ]:
            permission_classes = [IsAuthenticated, NotOrganizationCreator]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    @action(detail=True,
            methods=['post'],
            serializer_class=ReviewSerializer)
    def make_review(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['get'],
            serializer_class=ReviewSerializer)
    def get_reviews(self, request, pk):
        reviews = Review.objects.filter(organization_id=pk)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True,
            methods=['get'],
            serializer_class=OrderSerializer)
    def get_orders(self, request, pk):
        orders = Order.objects.filter(customer=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True,
            methods=['get'],
            serializer_class=OrderSerializer)
    def get_requested_orders(self, request, pk):
        requests = OrderRequest.objects.filter(performer=request.user)
        requested_orders_id = [req.order.id for req in requests]
        orders = Order.objects.filter(id__in=requested_orders_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            serializer_class=TokenSerializer)
    def confirm_email(self, request):
        organization = get_object_or_404(Organization, email=request.data['email'])
        token = request.data['token']
        if account_activation_token.check_token(organization, token):
            organization.is_active = True
            organization.save()
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'token is not valid'}, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Order, Organization


class IsOrderCreator(BasePermission):

    def has_permission(self, request, view):
        order = get_object_or_404(Order, pk=view.kwargs['pk'])
        return request.user == order.customer


class NotOrderCreator(BasePermission):

    def has_permission(self, request, view):
        order = get_object_or_404(Order, pk=view.kwargs['pk'])
        return request.user != order.customer


class IsOrganizationCreator(BasePermission):

    def has_permission(self, request, view):
        organization = get_object_or_404(Organization, pk=view.kwargs['pk'])
        return request.user == organization


class NotOrganizationCreator(BasePermission):

    def has_permission(self, request, view):
        organization = get_object_or_404(Organization, pk=view.kwargs['pk'])
        return request.user != organization

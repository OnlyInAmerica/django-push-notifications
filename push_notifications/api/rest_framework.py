from __future__ import absolute_import

import re

from rest_framework import permissions
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.viewsets import ModelViewSet

from push_notifications.models import APNSDevice, GCMDevice

HEX64_RE = re.compile("[0-9a-f]{64}", re.IGNORECASE)


# Serializers
class APNSDeviceSerializer(ModelSerializer):
    class Meta:
        model = APNSDevice
        exclude = ('user',)

    def validate_registration_id(self, value):
        # iOS device tokens are 256-bit hexadecimal (64 characters)

        if HEX64_RE.match(value) is None:
            raise ValidationError("Registration ID (device token) is invalid")
        return value


class GCMDeviceSerializer(ModelSerializer):
    class Meta:
        model = GCMDevice
        exclude = ('user',)


# Permissions
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # must be the owner to view the object
        return obj.user == request.user


# Mixins
class DeviceMixin(object):
    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            serializer.save(user=self.request.user)


class AuthorizedMixin(object):
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self):
        # filter all devices to only those belonging to the current user
        return self.queryset.filter(user=self.request.user)


# ViewSets
class APNSDeviceViewSet(DeviceMixin, ModelViewSet):
    queryset = APNSDevice.objects.all()
    serializer_class = APNSDeviceSerializer


class APNSDeviceAuthorizedViewSet(AuthorizedMixin, APNSDeviceViewSet):
    pass


class GCMDeviceViewSet(DeviceMixin, ModelViewSet):
    queryset = GCMDevice.objects.all()
    serializer_class = GCMDeviceSerializer


class GCMDeviceAuthorizedViewSet(AuthorizedMixin, GCMDeviceViewSet):
    pass

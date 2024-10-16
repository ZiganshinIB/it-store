from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ApprovalRoute, ApproveStep

from .serializers import ApprovalRouteSerializer, ApproveStepSerializer




# Create your tests here.

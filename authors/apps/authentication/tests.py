from django.db.utils import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import (
    User
)

class ModelTest(TestCase):

    def setUp(self):
        self.testUser = User(username='testuser',email='test@user.co', password='123456')

    def test_model_can_create_user(self):
        """This test checks if the model can create a user successfully"""
        oldCount = User.objects.count() #should be equal to 0
        self.testUser.save()

        newCount = User.objects.count()
        self.assertNotEqual(oldCount, newCount)

    def test_model_creates_unique_instances(self):
        """This tests if a unique user can be created"""
        self.testUser.save()
        newUser = User(username='testuser',email='another@test.user', password='123456')

        with self.assertRaises(IntegrityError):
            newUser.save()

    
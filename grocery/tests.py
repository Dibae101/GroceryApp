from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import GroceryItem, Group, Basket, BasketItem, GroupMembership

class GroceryItemModelTest(TestCase):
    def test_create_grocery_item(self):
        item = GroceryItem.objects.create(name="Apple", category="Fruit", price=1.50)
        self.assertEqual(item.name, "Apple")
        self.assertEqual(item.category, "Fruit")
        self.assertEqual(item.price, 1.50)

class GroupModelTest(TestCase):
    def test_create_group(self):
        group = Group.objects.create(name="Test Group")
        self.assertEqual(group.name, "Test Group")

class BasketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.basket = Basket.objects.create(user=self.user)
        self.item = GroceryItem.objects.create(name="Banana", category="Fruit", price=0.99)

    def test_add_item_to_basket(self):
        basket_item = BasketItem.objects.create(basket=self.basket, item=self.item, quantity=2)
        self.assertEqual(basket_item.quantity, 2)
        self.assertEqual(self.basket.total_cost(), Decimal('1.98'))

class GroupMembershipTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.group = Group.objects.create(name="Test Group")

    def test_join_group(self):
        membership = GroupMembership.objects.create(group=self.group, user=self.user)
        self.assertTrue(GroupMembership.objects.filter(group=self.group, user=self.user).exists())

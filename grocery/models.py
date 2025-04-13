from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    preferred_categories = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def avatar(self):
        # Generate a unique avatar identifier based on username
        return f"data:image/svg+xml,<svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'><rect width='100' height='100' fill='%238BB174'/><text x='50' y='50' font-size='50' text-anchor='middle' dy='.3em'>🥑</text></svg>"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class GroceryItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='GroupMembership', related_name='custom_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def can_iterate_user(self, iterator_user, target_user):
        """
        Check if iterator_user can iterate target_user in this group.
        Rules:
        1. Both users must be in the group
        2. Iterator must be an admin or the group creator
        3. Can't iterate yourself
        """
        if iterator_user == target_user:
            return False
            
        if iterator_user == self.created_by:
            return True
            
        try:
            iterator_membership = GroupMembership.objects.get(group=self, user=iterator_user)
            target_membership = GroupMembership.objects.get(group=self, user=target_user)
            return iterator_membership.is_admin
        except GroupMembership.DoesNotExist:
            return False

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=100, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    is_group_basket = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'group', 'is_group_basket')
    
    @property
    def total_cost(self):
        return self.basketitem_set.aggregate(
            total=Sum(F('quantity') * F('item__price'))
        )['total'] or 0
    
    @property
    def subtotal(self):
        return self.total_cost
    
    @property
    def delivery_fee(self):
        return 5.00 if self.subtotal < 50 else 0
    
    @property
    def total_with_delivery(self):
        return float(self.subtotal) + self.delivery_fee

    def __str__(self):
        if self.is_group_basket:
            return f"{self.group.name}'s Group Basket"
        return f"{self.user.username}'s Personal Basket"

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('basket', 'item')
    
    @property
    def total_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

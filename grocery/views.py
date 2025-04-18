from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
import decimal
from .models import GroceryItem, Basket, Group, BasketItem, GroupMembership, GroupInvitation

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard(request):
    page_number = request.GET.get('page', 1)
    items = GroceryItem.objects.all()
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    if query:
        items = items.filter(Q(name__icontains=query) | Q(category__icontains=query))

    if category_filter:
        items = items.filter(category__iexact=category_filter)

    paginator = Paginator(items, 12)  # Show 12 items per page
    page_obj = paginator.get_page(page_number)

    user_groups = Group.objects.filter(members=request.user)

    return render(request, 'dashboard.html', {
        'items': page_obj.object_list,
        'categories': GroceryItem.objects.values_list('category', flat=True).distinct(),
        'query': query,
        'category_filter': category_filter,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'user_groups': user_groups
    })

@login_required
def basket_view(request):
    basket = Basket.objects.filter(
        user=request.user,
        is_group_basket=False
    ).first()
    
    if basket:
        # Get all basket items with their calculated totals
        basket_items = []
        for item in basket.basketitem_set.all():
            basket_items.append({
                'item': item,
                'total_price': item.total_price
            })
        
        # Calculate totals using model properties
        basket_data = {
            'subtotal': basket.subtotal,
            'delivery_fee': basket.delivery_fee,
            'total_with_delivery': basket.total_with_delivery,
            'total_items': sum(item['item'].quantity for item in basket_items)
        }
    else:
        basket_items = []
        basket_data = None
    
    return render(request, 'basket.html', {
        'basket': basket,
        'basket_data': basket_data,
        'basket_items': basket_items
    })

@login_required
def add_to_basket(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    add_to_group = request.POST.get('add_to_group')
    group_id = request.POST.get('group_id')

    if add_to_group and group_id:
        group = get_object_or_404(Group, id=group_id)
        if not group.members.filter(id=request.user.id).exists():
            messages.error(request, "You're not a member of this group.")
            return redirect('dashboard')
        
        basket = Basket.objects.filter(
            group=group,
            is_group_basket=True
        ).first()
        
        if not basket:
            basket = Basket.objects.create(
                user=request.user,
                group=group,
                is_group_basket=True
            )
    else:
        basket = Basket.objects.filter(
            user=request.user,
            is_group_basket=False,
            group__isnull=True
        ).first()
        
        if not basket:
            basket = Basket.objects.create(
                user=request.user,
                is_group_basket=False
            )

    basket_item, created = BasketItem.objects.get_or_create(
        basket=basket,
        item=item,
        defaults={'quantity': 1}
    )
    
    if not created:
        basket_item.quantity += 1
        basket_item.save()

    messages.success(request, f'Added {item.name} to {"group" if add_to_group else "personal"} basket')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def add_to_list(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    add_to_group = request.POST.get('add_to_group')
    group_id = request.POST.get('group_id')

    if add_to_group and group_id:
        group = get_object_or_404(Group, id=group_id)
        if not group.members.filter(id=request.user.id).exists():
            messages.error(request, "You're not a member of this group.")
            return redirect('dashboard')

        basket = Basket.objects.filter(
            group=group,
            is_group_basket=True
        ).first()

        if not basket:
            basket = Basket.objects.create(
                user=request.user,
                group=group,
                is_group_basket=True
            )
    else:
        basket = Basket.objects.filter(
            user=request.user,
            is_group_basket=False,
            group__isnull=True
        ).first()

        if not basket:
            basket = Basket.objects.create(
                user=request.user,
                is_group_basket=False
            )

    basket_item, created = BasketItem.objects.get_or_create(
        basket=basket,
        item=item,
        defaults={'quantity': 1}
    )

    if not created:
        basket_item.quantity += 1
        basket_item.save()

    messages.success(request, f'Added {item.name} to {"group" if add_to_group else "personal"} list')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def remove_from_basket(request, item_id):
    group_id = request.POST.get('group_id')
    remove_all = request.POST.get('remove_all') == 'true'
    
    if group_id:
        group = get_object_or_404(Group, id=group_id)
        basket = get_object_or_404(Basket, group=group, is_group_basket=True)
    else:
        basket = get_object_or_404(Basket, user=request.user, is_group_basket=False)
    
    basket_item = get_object_or_404(BasketItem, basket=basket, item_id=item_id)
    
    if remove_all:
        basket_item.delete()
        messages.success(request, 'Item removed from basket.')
    else:
        if basket_item.quantity > 1:
            basket_item.quantity -= 1
            basket_item.save()
            messages.success(request, 'Item quantity reduced.')
        else:
            basket_item.delete()
            messages.success(request, 'Item removed from basket.')
    
    if group_id:
        return redirect('group_detail', group_id=group_id)
    return redirect('basket_view')

@login_required
def group_list(request):
    owned_groups = Group.objects.filter(created_by=request.user)
    member_groups = Group.objects.filter(members=request.user).exclude(created_by=request.user)
    return render(request, 'group_management.html', {
        'owned_groups': owned_groups,
        'member_groups': member_groups
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        if group_name:
            group = Group.objects.create(name=group_name, created_by=request.user)
            GroupMembership.objects.create(group=group, user=request.user, is_admin=True)
            messages.success(request, f'Group "{group_name}" created successfully!')
        else:
            messages.error(request, 'Please provide a group name')
    return redirect('group_list')

@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.created_by or GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
        group.delete()
        messages.success(request, 'Group deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this group.')
    return redirect('group_list')

@login_required
def invite_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
        messages.error(request, 'Only group admins can invite new members.')
        return redirect('group_detail', group_id=group_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if username:
            try:
                user = User.objects.get(username=username)
                if group.members.filter(id=user.id).exists():
                    messages.warning(request, f'{username} is already a member of this group.')
                    return redirect('group_detail', group_id=group_id)
                
                # Create invitation
                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(days=7)
                
                invitation = GroupInvitation.objects.create(
                    group=group,
                    email=user.email,
                    invited_by=request.user,
                    token=token,
                    expires_at=expires_at
                )

                # Send invitation email
                invitation_url = request.build_absolute_uri(
                    reverse('accept_invitation', args=[token])
                )
                send_mail(
                    subject=f'Invitation to join {group.name}',
                    message=f'{request.user.username} has invited you to join {group.name}. Click here to accept: {invitation_url}',
                    from_email='noreply@groceryapp.com',
                    recipient_list=[user.email],
                )
                messages.success(request, f'Invitation sent to {username}')
            except User.DoesNotExist:
                if email:
                    # If username doesn't exist but email is provided, send email invitation
                    token = str(uuid.uuid4())
                    expires_at = timezone.now() + timedelta(days=7)
                    
                    invitation = GroupInvitation.objects.create(
                        group=group,
                        email=email,
                        invited_by=request.user,
                        token=token,
                        expires_at=expires_at
                    )
                    
                    signup_url = request.build_absolute_uri(reverse('signup'))
                    invitation_url = request.build_absolute_uri(
                        reverse('accept_invitation', args=[token])
                    )
                    
                    send_mail(
                        subject=f'Invitation to join {group.name}',
                        message=f'{request.user.username} has invited you to join {group.name} on our platform.\n\n'
                               f'First, sign up here: {signup_url}\n'
                               f'Then click here to accept the invitation: {invitation_url}',
                        from_email='noreply@groceryapp.com',
                        recipient_list=[email],
                    )
                    messages.success(request, f'Invitation sent to {email}')
                else:
                    messages.error(request, f'User {username} not found. Please provide an email address to invite them.')

    return redirect('group_detail', group_id=group_id)

@login_required
def accept_invitation(request, token):
    invitation = get_object_or_404(GroupInvitation, token=token, accepted=False)
    
    if invitation.is_expired():
        messages.error(request, 'This invitation has expired.')
        return redirect('dashboard')
    
    if request.user.email != invitation.email:
        messages.error(request, 'This invitation was sent to a different email address.')
        return redirect('dashboard')
    
    GroupMembership.objects.get_or_create(
        group=invitation.group,
        user=request.user,
        defaults={'is_admin': False}
    )
    
    invitation.accepted = True
    invitation.save()
    
    messages.success(request, f'You have successfully joined {invitation.group.name}!')
    return redirect('group_detail', group_id=invitation.group.id)

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    is_member = group.members.filter(id=request.user.id).exists()
    is_admin = GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists()
    
    # Get group basket
    group_basket = None
    if is_member:
        group_basket = Basket.objects.filter(
            group=group,
            is_group_basket=True
        ).first()
        
        if not group_basket:
            group_basket = Basket.objects.create(
                user=request.user,
                group=group,
                is_group_basket=True
            )
    
    # Create invitation token and link if admin
    invite_link = None
    if is_admin:
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)
        invitation = GroupInvitation.objects.create(
            group=group,
            email='',  # Will be filled when used
            invited_by=request.user,
            token=token,
            expires_at=expires_at
        )
        invite_link = request.build_absolute_uri(
            reverse('accept_invitation', args=[token])
        )
    
    context = {
        'group': group,
        'is_member': is_member,
        'is_admin': is_admin,
        'group_basket': group_basket,
        'members': group.groupmembership_set.select_related('user').all(),
        'invite_link': invite_link,
    }
    
    return render(request, 'group_detail.html', context)

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        GroupMembership.objects.create(group=group, user=request.user)
        messages.success(request, f'You have successfully joined {group.name}!')
    else:
        messages.info(request, 'You are already a member of this group.')
    return redirect('group_detail', group_id=group_id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = get_object_or_404(GroupMembership, group=group, user=request.user)
    
    # Don't allow the last admin to leave
    if membership.is_admin and not GroupMembership.objects.filter(group=group, is_admin=True).exclude(user=request.user).exists():
        messages.error(request, 'Cannot leave group - you are the only admin.')
        return redirect('group_detail', group_id=group_id)
    
    membership.delete()
    messages.success(request, f'You have left {group.name}')
    return redirect('group_list')

@login_required
def toggle_admin(request, group_id, user_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
            messages.error(request, 'Only group admins can change member roles.')
            return redirect('group_detail', group_id=group_id)
        
        membership = get_object_or_404(GroupMembership, group=group, user_id=user_id)
        membership.is_admin = not membership.is_admin
        membership.save()
        
        action = 'added as' if membership.is_admin else 'removed as'
        messages.success(request, f'{membership.user.username} {action} admin.')
    
    return redirect('group_detail', group_id=group_id)

@login_required
def remove_member(request, group_id, user_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        if not GroupMembership.objects.filter(group=group, user=request.user, is_admin=True).exists():
            messages.error(request, 'Only group admins can remove members.')
            return redirect('group_detail', group_id=group_id)
        
        membership = get_object_or_404(GroupMembership, group=group, user_id=user_id)
        if membership.user == group.created_by:
            messages.error(request, 'Cannot remove the group creator.')
            return redirect('group_detail', group_id=group_id)
        
        membership.delete()
        messages.success(request, f'{membership.user.username} has been removed from the group.')
    
    return redirect('group_detail', group_id=group_id)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user

    if request.method == 'POST' and is_owner:
        profile_user.userprofile.bio = request.POST.get('bio', '')
        profile_user.userprofile.preferred_categories = request.POST.get('categories', '')
        profile_user.userprofile.save()
        messages.success(request, 'Profile updated successfully!')

    preferred_categories = profile_user.userprofile.preferred_categories.split(',') if profile_user.userprofile.preferred_categories else []

    return render(request, 'profile.html', {
        'user': profile_user,
        'is_owner': is_owner,
        'preferred_categories': preferred_categories,
    })

def grocery_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)

    items = GroceryItem.objects.all()

    if query:
        items = items.filter(Q(name__icontains=query) | Q(category__icontains=query))

    if category_filter:
        items = items.filter(category__iexact=category_filter)

    paginator = Paginator(items, 10)  # Show 10 items per page
    page_obj = paginator.get_page(page_number)

    return render(request, 'grocery_list.html', {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'category_filter': category_filter
    })

def grocery_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        
        if name and category and price:
            GroceryItem.objects.create(
                name=name,
                category=category,
                price=price,
                description=description,
                image_url=image_url
            )
            messages.success(request, f'Added {name} to grocery items')
        else:
            messages.error(request, 'Please fill in all required fields')
    return redirect('grocery_list')

def grocery_delete(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    item.delete()
    return redirect('grocery_list')

def groster_landing(request):
    return render(request, 'groster.html')

from django.core.management.base import BaseCommand
from grocery.models import GroceryItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import sample grocery items'

    def handle(self, *args, **options):
        # Sample grocery items with realistic data
        grocery_items = [
            {
                'name': 'Organic Bananas',
                'category': 'Fruits',
                'price': '2.99',
                'description': 'Fresh organic bananas, sold by the bunch',
                'image_url': 'https://images.unsplash.com/photo-1481349518771-20055b2a7b24'
            },
            {
                'name': 'Whole Milk',
                'category': 'Dairy',
                'price': '3.49',
                'description': '1 gallon of fresh whole milk',
                'image_url': 'https://images.unsplash.com/photo-1563636619-e9143da7973b'
            },
            {
                'name': 'Brown Eggs',
                'category': 'Dairy',
                'price': '4.99',
                'description': 'Dozen large brown eggs from free-range chickens',
                'image_url': 'https://images.unsplash.com/photo-1489726933853-010eb1484d1a'
            },
            {
                'name': 'Avocados',
                'category': 'Fruits',
                'price': '1.99',
                'description': 'Ripe Hass avocados',
                'image_url': 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578'
            },
            {
                'name': 'Baby Spinach',
                'category': 'Vegetables',
                'price': '3.99',
                'description': 'Fresh organic baby spinach, 5oz package',
                'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb'
            },
            {
                'name': 'Whole Grain Bread',
                'category': 'Bakery',
                'price': '3.99',
                'description': 'Fresh baked whole grain bread',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff'
            },
            {
                'name': 'Ground Coffee',
                'category': 'Beverages',
                'price': '9.99',
                'description': 'Premium arabica ground coffee, 12oz bag',
                'image_url': 'https://images.unsplash.com/photo-1497515114629-f71d768fd07c'
            },
            {
                'name': 'Red Bell Peppers',
                'category': 'Vegetables',
                'price': '1.29',
                'description': 'Fresh red bell peppers',
                'image_url': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83'
            },
            {
                'name': 'Greek Yogurt',
                'category': 'Dairy',
                'price': '4.99',
                'description': 'Plain Greek yogurt, 32oz container',
                'image_url': 'https://images.unsplash.com/photo-1571217668979-f46db8864f75'
            },
            {
                'name': 'Honey',
                'category': 'Pantry',
                'price': '7.99',
                'description': 'Raw organic honey, 16oz jar',
                'image_url': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc'
            },
            {
                'name': 'Chicken Breast',
                'category': 'Meat',
                'price': '8.99',
                'description': 'Fresh boneless skinless chicken breast, per pound',
                'image_url': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791'
            },
            {
                'name': 'Salmon Fillet',
                'category': 'Seafood',
                'price': '12.99',
                'description': 'Fresh Atlantic salmon fillet, per pound',
                'image_url': 'https://images.unsplash.com/photo-1580476262798-bddd9f4b7369'
            },
            {
                'name': 'Sweet Potatoes',
                'category': 'Vegetables',
                'price': '1.49',
                'description': 'Fresh sweet potatoes, per pound',
                'image_url': 'https://images.unsplash.com/photo-1596097635121-14b63b7a0c16'
            },
            {
                'name': 'Quinoa',
                'category': 'Grains',
                'price': '5.99',
                'description': 'Organic quinoa, 16oz package',
                'image_url': 'https://images.unsplash.com/photo-1612358405970-e1afd02b0897'
            },
            {
                'name': 'Almonds',
                'category': 'Nuts',
                'price': '8.99',
                'description': 'Raw almonds, 12oz bag',
                'image_url': 'https://images.unsplash.com/photo-1508061125266-f9772ebe057f'
            }
        ]

        for item in grocery_items:
            GroceryItem.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': item['category'],
                    'price': Decimal(item['price']),
                    'description': item['description'],
                    'image_url': item['image_url']
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added {item["name"]}'))
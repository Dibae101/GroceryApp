from django.core.management.base import BaseCommand
from grocery.models import GroceryItem
import requests
import json

class Command(BaseCommand):
    help = 'Import grocery items from Open Food Facts API'

    def handle(self, *args, **kwargs):
        self.stdout.write('Importing grocery items...')
        
        # Using Open Food Facts API to get common grocery items
        categories = ['beverages', 'snacks', 'dairy', 'fruits', 'vegetables']
        
        for category in categories:
            url = f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={category}&search_simple=1&action=process&json=1&page_size=20'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                for product in data.get('products', []):
                    name = product.get('product_name_en', '')
                    if name:
                        # Get or create to avoid duplicates
                        GroceryItem.objects.get_or_create(
                            name=name[:100],  # Limiting name length
                            defaults={
                                'category': category.title(),
                                'price': round(float(product.get('nutriments', {}).get('energy-kcal', 0)) / 100, 2) or 4.99,  # Using energy value to generate a mock price
                                'description': product.get('generic_name_en', '')[:200]  # Limiting description length
                            }
                        )
            
        self.stdout.write(self.style.SUCCESS('Successfully imported grocery items'))
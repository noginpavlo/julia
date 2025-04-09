import os
import django
import sys
from django.conf import settings

# Set the default settings module for Django
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")

# Initialize Django
django.setup()

# Your logic here
if not settings.configured:
    print("Django settings are not configured")

# Now import your models
from card_manager.models import JuliaTest

def save_data(array):
    print("save_data called!")
    if len(array) == 6:
        # Create a new record in the JuliaTest table using Django ORM
        JuliaTest.objects.create(
            date=array[0],
            word=array[1],
            phonetics=array[2],
            definition=array[3],
            example=array[4],
            increment=array[5]
        )
        print(f"Successfully recorded data for word '{array[1]}'")
        return "Success"
    else:
        return "Invalid input array length"

# Generated migration to delete old unused models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('combine', '0003_model'),
    ]

    operations = [
        # First remove the virtual_try_on FK from Model
        migrations.RemoveField(
            model_name='model',
            name='virtual_try_on',
        ),
        # Delete OutfitFavorite which depends on Outfit
        migrations.DeleteModel(
            name='OutfitFavorite',
        ),
        # Delete VirtualTryOn which depends on Outfit
        migrations.DeleteModel(
            name='VirtualTryOn',
        ),
        # Delete OutfitClothes which depends on Outfit
        migrations.DeleteModel(
            name='OutfitClothes',
        ),
        # Finally delete Outfit
        migrations.DeleteModel(
            name='Outfit',
        ),
    ]

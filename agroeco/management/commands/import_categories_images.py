import os
from io import BytesIO
import time

import logging

from google_images_search import GoogleImagesSearch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.management.base import BaseCommand

from saleor.product.models import Category

logger = logging.getLogger(__name__)

gis = GoogleImagesSearch(settings.GOOGLE_DEV_API_KEY,settings.GOOGLE_PROJECT_CX)

class Command(BaseCommand):

    help = "Update categories images downloaded from the internet."

    def add_arguments(self, parser):
        parser.add_argument('category_name', nargs='*', type=str)

    def update_or_create_category_image(self, category):

        gis.search({
            'q': '{}'.format(category.name),
            'imgSize': 'xxlarge',
            'num': 1
        })

        for image in gis.results():

            _, file_extension = os.path.splitext(image.url)

            bytes_io = BytesIO()
            image.copy_to(bytes_io)

            bytes_io.seek(0)
            category.background_image = SimpleUploadedFile(
                '{}{}'.format(category.slug, file_extension),
                bytes_io.read()
            )

            category.save()

    def import_categories_images(self, categories_names):
        
        if len(categories_names) == 0:
            q = Category.objects.all()
        else:
            q = Category.objects.filter(name__in=categories_names)

        for c in q:
            try:
                self.update_or_create_category_image(c)
            except Exception:
                print('Error en categoría {}.'.format(c))

    def handle(self, *args, **options):

        self.stdout.write('Update categories using file as input.')

        self.import_categories_images(options['category_name'])

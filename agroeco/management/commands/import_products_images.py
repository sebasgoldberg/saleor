import os
from io import BytesIO
import time

import logging

from google_images_search import GoogleImagesSearch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.management.base import BaseCommand

from saleor.product.models import Product

logger = logging.getLogger(__name__)

gis = GoogleImagesSearch(settings.GOOGLE_DEV_API_KEY,settings.GOOGLE_PROJECT_CX)

class Command(BaseCommand):

    help = "Update products images downloaded from the internet."

    def add_arguments(self, parser):
        parser.add_argument('product_name', nargs='*', type=str)

    def update_or_create_product_image(self, product):

        gis.search({
            'q': '{} {}'.format(product.get_slug(), product.category.slug),
            'imgSize': 'large',
            'num': 1
        })

        for image in gis.results():

            product_image, _ = product.images.get_or_create()

            _, file_extension = os.path.splitext(image.url)

            bytes_io = BytesIO()
            image.copy_to(bytes_io)

            bytes_io.seek(0)
            product_image.image = SimpleUploadedFile(
                '{}-{}{}'.format(product.category.slug, product.get_slug(), file_extension),
                bytes_io.read()
            )

            product_image.save()

    def import_products_images(self, products_names):
        
        if len(products_names) == 0:
            q = Product.objects.all()
        else:
            q = Product.objects.filter(name__in=products_names)

        for p in q:
            try:
                self.update_or_create_product_image(p)
            except Exception:
                print('Error en producto {}.'.format(p))

    def handle(self, *args, **options):

        self.stdout.write('Update products using file as input.')

        self.import_products_images(options['product_name'])

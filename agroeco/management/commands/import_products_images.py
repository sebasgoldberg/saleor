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

        parser.add_argument('--num', type=int, nargs='?', default=1,
            help='Number of images per product',
        )

    def update_or_create_product_image(self, product, num):

        gis.search({
            'q': '{} {}'.format(product.get_slug(), product.category.slug),
            'imgSize': 'large',
            'num': num
        })

        product_images = [ image for image in product.images.all() ]

        for image in gis.results():

            product_image = ( 
                product.images.create() if len(product_images) == 0 
                else product_images.pop(0) 
                )
                
            _, file_extension = os.path.splitext(image.url)

            bytes_io = BytesIO()
            image.copy_to(bytes_io)

            bytes_io.seek(0)
            product_image.image = SimpleUploadedFile(
                '{}-{}{}'.format(product.category.slug, product.get_slug(), file_extension),
                bytes_io.read()
            )

            product_image.save()

    def import_products_images(self, products_names, num):
        
        if len(products_names) == 0:
            q = Product.objects.all()
        else:
            q = Product.objects.filter(name__in=products_names)

        for p in q:
            try:
                self.update_or_create_product_image(p, num)
            except Exception:
                print('Error en producto {}.'.format(p))

    def handle(self, *args, **options):

        self.stdout.write('Update products using file as input.')

        self.import_products_images(options['product_name'], options['num'])

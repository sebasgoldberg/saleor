import logging

from django.utils.text import slugify
from django.db import transaction

from django.core.management.base import BaseCommand
from tqdm import tqdm

from saleor.product.models import *

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = "Update products using file as input."

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def get_product_type_name(self, **attributes):

        res = []

        if 'Tipo' in attributes.keys() and attributes['Tipo']:
            res.append('Tipificado')
        if 'Marca' in attributes.keys() and attributes['Marca']:
            res.append('Con Marca')
        if 'Envase' in attributes.keys() and attributes['Envase']:
            res.append('Retornable')
        if 'Medida' in attributes.keys() and attributes['Medida']:
            res.append('Medible')
        
        return ' '.join(res)

    def import_product(self, product_name, category_name, product_price_amount, 
            variant_price_amount, stock, is_published, **attributes):

        with transaction.atomic():

            product_type, _ = ProductType.objects.get_or_create(
                name=self.get_product_type_name(**attributes))

            category, _ = Category.objects.get_or_create(name=category_name, defaults={ 'slug': slugify(category_name) })

            product, _ = Product.objects.update_or_create(
                name=product_name,
                defaults={
                    'product_type': product_type,
                    'category': category,
                    'price_amount': product_price_amount,
                    'is_published': is_published
                })

            attributes_values = [v for v in attributes.values() if v]

            product_variant, _ = ProductVariant.objects.update_or_create(
                sku='-'.join(slugify(x) for x in ([product_name]+attributes_values)),
                defaults={
                    'name': ' / '.join(attributes_values),
                    'price_override_amount': variant_price_amount,
                    'product': product,
                    'quantity': stock,
                    'cost_price_amount': None,
                    'weight': None
                })

            for attribute_name, attribute_value in attributes.items():

                if not attribute_value:
                    continue

                attribute, _ = Attribute.objects.update_or_create(
                    name=attribute_name, 
                    defaults={
                        'slug': slugify(attribute_name),
                        'input_type': AttributeInputType.DROPDOWN,
                    })

                value, _ = attribute.values.get_or_create(
                    name=attribute_value,
                    defaults={ 
                        'value': attribute_value, 
                        'slug': slugify(attribute_value) 
                    })


                product_type_attr_variant, _ = product_type.attributevariant.get_or_create(attribute=attribute)

                # Creamos la asignación de valor para el atributo a nivel de variante.
                assigned_varian_attribute, _ = AssignedVariantAttribute.objects.get_or_create(variant=product_variant, assignment=product_type_attr_variant)

                # E indicamos su valor.
                assigned_varian_attribute.values.set([value])


    def import_products(self, filename):
        
        line_num = 0
        with open(filename, encoding='utf-16') as f:
            for line in f:
                line_num += 1
                if line_num < 2:
                    continue
                reg = [ x.strip() for x in line.split("\t") ]

                self.import_product(
                    product_name=reg[0], category_name=reg[1],
                    product_price_amount=Decimal(reg[9]), variant_price_amount=Decimal(reg[7]),
                    stock=reg[8], is_published=bool(reg[11]),
                    Tipo=reg[2], Marca=reg[3], Envase=reg[5], Medida=reg[6]
                    )

    def handle(self, *args, **options):

        self.stdout.write('Update products using file as input.')

        for filename in options['filename']:

            self.import_products(filename)

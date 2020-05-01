import os

from io import BytesIO

from PIL import Image

from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.core.files import File

from django.conf import settings

from saleor.product.models import ProductImage

def square(im, fill_color=(255, 255, 255, 255)):

    x, y = im.size
    size = max(x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im

    # width, height = img.size

    # if width == height:
    #     return

    # x0, x1, y0, y1 = (0, width, 0, height)

    # if width > height:
    #     x0 = (width - height)/2
    #     x1 = width - x0
    # else:
    #     y0 = (height - width)/2
    #     y1 = height - x0
    
    # return img.crop((x0, y0, x1, y1))

def add_marca(img):

    marca = Image.open(os.path.join(settings.PROJECT_ROOT, 'agroeco', 'marca-foto.png'))

    xm, ym, = marca.size
    xi, yi = img.size

    x = int(( xi - xm ) / 2)

    img.paste(marca, (x, 0), marca)


def square_and_resize(image_field, size=512):

    img = Image.open(image_field)

    img = square(img)

    img = img.resize((size,size), Image.ANTIALIAS)

    add_marca(img)

    thumb_io = BytesIO()

    img.save(thumb_io, 'PNG', quality=85)

    return File(thumb_io, name=(image_field.name))

@receiver(pre_save, sender=ProductImage)
def my_handler(sender, instance, raw, **kwargs):

    if raw:
        return

    instance.image = square_and_resize(instance.image)

    pass

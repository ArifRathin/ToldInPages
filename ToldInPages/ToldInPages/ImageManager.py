from PIL import Image
from io import BytesIO
from django.core.files import File


def getProcessedImage(request, photo):
    im = Image.open(photo)
    w = im.width
    h = im.height
    if w>=h:
        factor = round(w/h,2)
        if w>1500 and w<=3000:
            w //= 2
        elif w>3000 and w<=5000:
            w //= 3
        elif w>5000 or w>5000:
            w //= 4
        h = int(w//factor)
    else:
        factor = round(h/w,2)
        if h>1500 and h<=3000:
            h //= 2
        elif h>3000 and h<=5000:
            h //= 3
        elif h>5000 or h>5000:
            h //= 4
        w = int(h//factor)
    size = (w,h)
    im = im.resize(size)
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality=23)
    new_image = File(im_io, name=photo.name)
    return new_image
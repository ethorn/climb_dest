from PIL import Image

import os
import time


def create_image_set(image_dir, image_name):

    start = time.time()

    # Bilderna behåller sin aspect ratio, och resizes till at bredden eller höjden max det under:
    # 960x500 blir till 540x300, 768x411, .....
    mini = 250, 250
    thumb = 392, 392
    small = 600, 600
    medium = 900, 900
    large = 1200, 1200

    image = Image.open(os.path.join(image_dir, image_name))

    image_ext = image_name.split(".")[-1]
    image_name = image_name.split(".")[0]

    # MINI ###
    mini_image = image.copy()
    mini_image.thumbnail(mini, Image.LANCZOS)
    mini_image.save(f"{os.path.join(image_dir, image_name)}-mini.{image_ext}", optimize=True, quality=95)

    # THUMBNAIL ###
    thumbnail_image = image.copy()
    thumbnail_image.thumbnail(thumb, Image.LANCZOS)
    thumbnail_image.save(f"{os.path.join(image_dir, image_name)}-thumbnail.{image_ext}", optimize=True, quality=95)

    # SMALL ###
    small_image = image.copy()
    small_image.thumbnail(small, Image.LANCZOS)
    small_image.save(f"{os.path.join(image_dir, image_name)}-540.{image_ext}", optimize=True, quality=95)

    # MEDIUM ###
    medium_image = image.copy()
    medium_image.thumbnail(medium, Image.LANCZOS)
    medium_image.save(f"{os.path.join(image_dir, image_name)}-768.{image_ext}", optimize=True, quality=95)

    # LARGE ###
    large_image = image.copy()
    large_image.thumbnail(large, Image.LANCZOS)
    large_image.save(f"{os.path.join(image_dir, image_name)}-1080.{image_ext}", optimize=True, quality=95)

    end = time.time()

    time_elapsed = end - start

    print(f"Task complete in: {time_elapsed}")

    return True

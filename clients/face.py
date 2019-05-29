# get_bounding_rect
import cv2
from pathlib import Path

image_dir = '../python-server/uploads/'


def yield_images_from_dir(image_dir):
    image_dir = Path(image_dir)
    for image_path in image_dir.glob("*.*"):
        img = cv2.imread(str(image_path), 1)
        if img is not None:
            h, w, _ = img.shape
            r = 640 / max(w, h)
            yield (cv2.resize(img, (int(w * r), int(h * r))), image_path)


image_generator = yield_images_from_dir(image_dir)

img_size = 64
top = 147
bottom = 214
left = 382
right = 449

for (img, name) in image_generator:
    print(str(name))
    face = cv2.resize(img[top:bottom, left:right, :], (img_size, img_size))
    cv2.imshow(str(name), face)
    cv2.waitKey(10000)
    print("done")

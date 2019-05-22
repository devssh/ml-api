methods = {
    "get_bounding_rect": {
        "url": "/face/get_bounding_rects",
        "http_methods": ["POST"]
    }
}

import sys
sys.path.insert(0, 'models')
from wide_resnet import WideResNet

img_size = 64
depth = 16
k = 8
model = WideResNet(img_size, depth=depth, k=k)()
model.load_weights("models/weights.28-3.73.hdf5")

def get_bounding_rect():
    from pathlib import Path
    import cv2
    import dlib
    import numpy as np
    import pandas as pd
    request_data = dict(request.form)
    if not "c9095970345d" in request_data["auth"]:
        return "Incorrect authentication"
    def yield_images_from_dir(image_dir):
        image_dir = Path(image_dir)
        for image_path in image_dir.glob("*.*"):
            img = cv2.imread(str(image_path), 1)
            if img is not None:
                h, w, _ = img.shape
                r = 640 / max(w, h)
                yield (cv2.resize(img, (int(w * r), int(h * r))), image_path)
    margin = 0.4
    image_dir = "uploads/"
    # for face detection
    detector = dlib.get_frontal_face_detector()
    # load model and weights
    image_generator = yield_images_from_dir(image_dir) if image_dir else yield_images()
    total = 0
    recog_count = 0
    bounding_rects = []
    for (img, name) in image_generator:
        input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_h, img_w, _ = np.shape(input_img)
        # detect faces using dlib detector
        detected = detector(input_img, 1)
        faces = []
        total = total + 1
        if len(detected) > 0:
            recog_count = recog_count + 1
            for i, d in enumerate(detected):
                x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                xw1 = max(int(x1 - margin * w), 0)
                yw1 = max(int(y1 - margin * h), 0)
                xw2 = min(int(x2 + margin * w), img_w - 1)
                yw2 = min(int(y2 + margin * h), img_h - 1)
                faces = [*faces, [yw1, yw2 + 1, xw1, xw2 + 1, str(name), img_h, img_w]]
            bounding_rects = [*bounding_rects, *faces]
    return jsonify({"dlib_frontal_detector": json.loads(pd.DataFrame(bounding_rects, columns=["top", "bottom", "left", "right", "name", "height", "width"]).to_json(orient="records"))})

import numpy as np
import pandas as pd

# from tqdm import tqdm
# tqdm.pandas()
np.random.seed(7)

import tensorflow as tf

load_model = tf.keras.models.load_model
adam = tf.keras.optimizers.Adam(lr=1e-3)

import re


def string_vectorizer(strng, alphabet, max_str_len=20, gender=True):
    if (gender):
        strng = re.sub(r"[^a-z]+", "", strng.lower())
    else:
        strng = re.sub(r"[^a-zA-z0-9-]+", "", strng)
    vector = [[0 if char != letter else 1 for char in alphabet] for letter in strng[0:max_str_len]]
    while len(vector) != max_str_len:
        vector = [*vector, [0 for char in alphabet]]
    return np.array(vector)


gendermodel = load_model("models/gendermodel.h5")
gendermodel.load_weights("models/genderweights.h5")
gendermodel.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
# 90% accuracy on 30k female and 33k male names synthesised from Indian names list
gendermodel.summary()

methods = {
    "predict_from_name_tf": {
        "url": "/gender/extract_from_name",
        "http_methods": ["POST"]
    },
    "predict_from_image_tf": {
        "url": "/gender/extract_from_image",
        "http_methods": ["POST"]
    },
}

import gender_service


def predict_from_name_tf():

    request_data = json.loads(list(request.form.keys())[0])
    name_string = request_data["names"]

    if not "c9095970345d" in request_data["auth"]:
        return "Incorrect authentication"
    import numpy as np
    import pandas as pd
    import string
    alphabet_list = list(string.ascii_lowercase)
    max_name_len = 20


    names = pd.Series(list(filter(len, name_string.split(","))))
    names_transform = names.apply(
        lambda name: gender_service.string_vectorizer(name, alphabet_list, max_name_len).reshape(1, 20, 26))
    names_transform = np.vstack(names_transform.tolist())
    prediction = gender_service.gendermodel.predict(names_transform)
    prediction = [[int(pred[0] * 100) / 100, int(pred[1] * 100) / 100] for pred in prediction]
    return jsonify(
        {"names": name_string, "syntax": ["male_prob", "female_prob"], "predictions": np.array(prediction).tolist()})




def predict_from_image_tf():
    import datetime

    from pathlib import Path
    import cv2
    import dlib
    import numpy as np
    import pandas as pd
    import argparse
    from contextlib import contextmanager
    import sys
    sys.path.insert(0, 'models')

    request_data = dict(request.form)

    if not "c9095970345d" in request_data["auth"]:
        return "Incorrect authentication"


    from werkzeug import secure_filename
    file = request.files['pimage']
    if file:
        filename = secure_filename(file.filename)
        file.save("uploads/" + filename)


    from wide_resnet import WideResNet

    def get_time_now():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale=1, thickness=2):
        size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        x, y = point
        cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
        cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)

    def yield_images_from_dir(image_dir):
        image_dir = Path(image_dir)

        for image_path in image_dir.glob("*.*"):
            img = cv2.imread(str(image_path), 1)

            if img is not None:
                h, w, _ = img.shape
                r = 640 / max(w, h)
                yield (cv2.resize(img, (int(w * r), int(h * r))), image_path)

    depth = 16
    k = 8
    margin = 0.4

    def predict_images():
        image_dir = "uploads/"

        # for face detection
        detector = dlib.get_frontal_face_detector()

        # load model and weights
        img_size = 64
        model = WideResNet(img_size, depth=depth, k=k)()
        model.load_weights("models/weights.28-3.73.hdf5")

        image_generator = yield_images_from_dir(image_dir) if image_dir else yield_images()
        preds = []
        total = 0
        recog_count = 0
        for (img, name) in image_generator:
            input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_h, img_w, _ = np.shape(input_img)

            # detect faces using dlib detector
            detected = detector(input_img, 1)
            faces = np.empty((len(detected), img_size, img_size, 3))
            total = total + 1
            if len(detected) > 0:
                recog_count = recog_count + 1
                for i, d in enumerate(detected):
                    x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                    xw1 = max(int(x1 - margin * w), 0)
                    yw1 = max(int(y1 - margin * h), 0)
                    xw2 = min(int(x2 + margin * w), img_w - 1)
                    yw2 = min(int(y2 + margin * h), img_h - 1)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
                    faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

                # predict ages and genders of the detected faces
                results = model.predict(faces)
                predicted_genders = results[0]
                prediction = 1 - min([pred[1] for pred in predicted_genders])
                for pred in predicted_genders:
                    if (pred[0] > pred[1]):
                        prediction = pred[0]
                        break

                preds = [*preds, (prediction, str(name))]

        df = pd.DataFrame(preds, columns=["pred", "screen_name"])
        df["screen_name"] = df["screen_name"].apply(
            lambda x: ".png".join(x.split("uploads/", 1)[1].split(".png")[0:-1]))
        df["pred"] = df["pred"].apply(lambda x: x)
        return jsonify({"results": json.loads(df.to_json(orient="records")), "syntax": ["m_pred", "0", "w_pred", "1"]})

    return predict_images()


def upload_image():
    from werkzeug import secure_filename
    file = request.files['pimage']
    if file:
        filename = secure_filename(file.filename)
        file.save("uploads/" + filename)
        return 'Uploaded file'
    # return send_file(filename, mimetype='image/png')
    return "Error: No file found"

from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import sys
import logging

host = "0." + "0.0.0"
show_output = True

app = Flask(__name__)
# CORS(app, resources={r"*": {"origins": "*"}})
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Server started successfully')

sys.path.insert(0, 'serverless')

import email_service
import gender_service
import test_health


@app.route(email_service.methods["register"]["url"], methods=email_service.methods["register"]["http_methods"])
def register(twemail):
    import uuid
    email_service.send_mail(twemail, "TW ML API registration", "",
                            "To complete registration use the code " + uuid.uuid4().hex)
    return "Check email to complete verification"


@app.route(gender_service.methods["predict_from_name_tf"]["url"], methods=gender_service.methods["predict_from_name_tf"]["http_methods"])
def predict_from_name_tf():
    import numpy as np
    request_data = json.loads(list(request.form.keys())[0])
    name_string = request_data["names"]

    names = pd.Series(list(filter(len, name_string.split(","))))
    names_transform = names.apply(lambda name: gender_service.string_vectorizer(name, alphabet_list, max_name_len).reshape(1, 20, 26))
    names_transform = np.vstack(names_transform.tolist())
    prediction = gender_service.gendermodel.predict(names_transform)
    # print("array([[male, female]]) probability")
    prediction = [[int(pred[0]*100)/100, int(pred[1]*100)/100] for pred in prediction]
    return np.array(prediction)


@app.route(test_health.methods["testHealth"]["url"], methods=test_health.methods["testHealth"]["http_methods"])
def testHealth():
    # request.headers.get('')
    # request.args.get('')
    # data = json.loads(list(request.form.keys())[0])
    return "Python server is up"


if __name__ == '__main__':
    app.run(host=host, port=5001, debug=show_output)


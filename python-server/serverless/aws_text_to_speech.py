methods = {
    "aws_polly": {
        "url": "/aws/speech",
        "http_methods": ["POST"]
    },
    "aws_polly_char_count": {
        "url": "/aws/polly-count",
        "http_methods": ["POST"]
    }
}

character_count = 0


def aws_polly():
    request_data = json.loads(list(request.form.keys())[0])
    auth = request_data["auth"]
    if not "c9095970345dx" in request_data["auth"]:
        return "Incorrect authentication"
    text = utils.remove_quotes(str(request_data["Text"]))

    aws_text_to_speech.increment_char_count(text)
    output = utils.get_cli_output("aws polly synthesize-speech " +
                                  "--output-format \"mp3" + "\" " +
                                  "--voice-id \"Joanna" + "\" " +
                                  "--text \"" + text + "\" output.mp3")
    utils.get_cli_output("mv output.mp3 models/output.mp3")
    return send_file('output.mp3', mimetype='audio/mpeg')


def increment_char_count(text):
    global character_count
    if character_count > 4000000:
        raise ValueError("Rate limit exceeded")
    character_count = character_count + len(text)


def aws_polly_char_count():
    return str(aws_text_to_speech.character_count)

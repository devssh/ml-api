methods = {
    "aws_translate_text": {
        "url": "/aws/translate",
        "http_methods": ["POST"]
    },
    "aws_char_count": {
        "url": "/aws/translate-count",
        "http_methods": ["POST"]
    }
}

character_count = 0


def aws_translate_text():
    request_data = json.loads(list(request.form.keys())[0])
    auth = request_data["auth"]
    if not "c9095970345d" in request_data["auth"]:
        return "Incorrect authentication"
    text = utils.remove_quotes(str(request_data["Text"]))
    source = utils.remove_quotes(str(request_data["SourceLanguageCode"]))
    target = utils.remove_quotes(str(request_data["TargetLanguageCode"]))

    aws_translate.increment_char_count(text)
    output = utils.get_cli_output("aws translate translate-text " +
                                  "--source-language-code \"" + source + "\" " +
                                  "--target-language-code \"" + target + "\" " +
                                  "--text \"" + text + "\"")

    return output


def increment_char_count(text):
    global character_count
    character_count = character_count + len(text)


def aws_char_count():
    return str(aws_translate.character_count)

# {
#     "Text": "Buongiorno",
#     "SourceLanguageCode": "it",
#     "TargetLanguageCode": "en"
# }

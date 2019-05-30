methods = {
    "aws_transcribe": {
        "url": "/aws/speech_to_text",
        "http_methods": ["POST"]
    }
}

character_count = 0


def aws_transcribe():
    request_data = dict(request.form)
    auth = request_data["auth"]
    if not "c9095970345dx" in request_data["auth"]:
        return "Incorrect authentication"
    gender_service.upload_image(request, "models/")
    import uuid
    random_uuid = str(uuid.uuid4())
    transcribe_config = "{\"TranscriptionJobName\": \"" + random_uuid + "\", \"LanguageCode\": \"en-US\", \"MediaFormat\": \"mp3\", \"Media\": {\"MediaFileUri\": \"s3://mlapiaudio/audio.mp3\"}}"
    file = open("models/transcribe.json", "w")
    file.write(transcribe_config)
    file.close()
    utils.get_cli_output("aws s3 rm s3://mlapiaudio/audio.mp3")
    utils.get_cli_output("aws s3 cp models/audio.mp3 s3://mlapiaudio/")
    utils.get_cli_output(
        "aws transcribe start-transcription-job --region \"us-west-2\" --cli-input-json file://models/transcribe.json")
    output_url = {"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}}
    while output_url["TranscriptionJob"]["TranscriptionJobStatus"] not in "COMPLETED":
        app.logger.debug(output_url["TranscriptionJob"])
        output_url = json.loads(utils.get_cli_output(
            "aws transcribe get-transcription-job --region \"us-west-2\" --transcription-job-name \"" + random_uuid + "\""))
        import time
        time.sleep(5)
        app.logger.debug("waiting")
    output = utils.get_cli_output(
        "curl -XGET '" + output_url["TranscriptionJob"]["Transcript"]["TranscriptFileUri"] + "'")
    return output


def increment_char_count(text):
    global character_count
    if character_count > 4000000:
        raise ValueError("Rate limit exceeded")
    character_count = character_count + len(text)


def aws_transcribe_char_count():
    return str(aws_transcribe.character_count)

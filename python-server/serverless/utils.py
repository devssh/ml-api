methods = {"testHealth": {
    "url": "/testHealth",
    "http_methods": ["GET", "POST"]
}
}


def testHealth():
    # request.headers.get('')
    # request.args.get('')
    # data = json.loads(list(request.form.keys())[0])
    return "Python server is up"


def get_cli_output(cmd):
    import subprocess
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode("utf-8")


def remove_quotes(some_str):
    return some_str.replace("\"", "")

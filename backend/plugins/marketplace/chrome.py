import webbrowser


def register(registry):
    registry["open_url"] = open_url


def open_url(url):

    if not url.startswith("http"):
        url = "https://www.google.com/search?q=" + url

    webbrowser.open(url)

    return f"Abriendo {url}"

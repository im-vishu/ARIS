import webbrowser

def open_website(url: str) -> dict:
    ok = webbrowser.open(url)
    return {"success": bool(ok), "url": url}
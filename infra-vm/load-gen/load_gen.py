import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://nginx/"

def attack():
    while True:
        try:
            requests.post(URL + "submit", data={
                "name": "Bot", "email": "a@b.com", "message": "X" * 1000
            })
        except:
            pass

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as executor:
        for _ in range(3):
            executor.submit(attack)
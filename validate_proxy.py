import queue
import threading

import requests

q = queue.Queue()
valid_proxies = set()  # Shared set for storing valid proxies
lock = threading.Lock()  # Lock to synchronize access to the shared set

# Read proxies from file and populate the queue
with open("proxy_list.txt", 'r') as f:
    proxies = f.read().splitlines()
    for p in proxies:
        q.put(p)


def check_proxy():
    global q, valid_proxies
    while not q.empty():
        proxy = q.get()
        try:
            r_ip_check = requests.get("https://ipinfo.io/json",
                                      proxies={'http': proxy, 'https': proxy}, timeout=1)
        except Exception:
            continue

        if r_ip_check.status_code == 200:
            print(f"Working proxy: {proxy}")
            # Add the valid proxy to the shared set
            with lock:
                valid_proxies.add(proxy)


# Create and start 20 threads
threads = []
for _ in range(100):
    thread = threading.Thread(target=check_proxy)
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# After all threads are done, write the valid proxies to a file
with open("working_proxies.txt", 'w') as f:
    for proxy in valid_proxies:
        f.write(proxy + "\n")

print("Finished writing valid proxies to file.")

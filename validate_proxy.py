import queue
import threading

import requests

q = queue.Queue()
valid_proxies = set()
lock = threading.Lock()


def get_proxies(page=1):
    try:
        get_proxy_req = requests.get(
            f"https://proxylist.geonode.com/api/proxy-list?limit=500&page={page}&sort_by=lastChecked&sort_type=desc", timeout=2)
        get_proxy_req.raise_for_status()
        for p in get_proxy_req.json()['data']:
            if 'http' in p['protocols']:
                ip = f"{p['ip']}:{p['port']}"
                q.put(ip)
    except requests.RequestException:
        return


def check_proxy():
    while not q.empty():
        proxy = q.get()
        try:
            r_ip_check = requests.get("https://ipinfo.io/json",
                                      proxies={'http': proxy}, timeout=1)
            if r_ip_check.status_code == 200:
                with lock:
                    print(proxy)
                    valid_proxies.add(proxy)
        except requests.RequestException:
            return


if __name__ == '__main__':
    get_proxies_threads = []
    page = 1
    for _ in range(10):
        thread = threading.Thread(target=get_proxies, args=(page,))
        get_proxies_threads.append(thread)
        thread.start()
        page += 1
    for t in get_proxies_threads:
        t.join()

    check_proxy_threads = []
    for _ in range(100):
        thread = threading.Thread(target=check_proxy)
        check_proxy_threads.append(thread)
        thread.start()
    for thread in check_proxy_threads:
        thread.join()

    if len(valid_proxies) > 20:
        with open("working_proxies.txt", 'w') as f:
            for proxy in valid_proxies:
                f.write(proxy + "\n")
            print("Finished writing valid proxies to file.")

import requests
r = requests.post("https://httpbin.org/post", data={"a": 1}, timeout=10)
print(r.json()["headers"]["Content-Type"])
print(r.json()["form"])
print(r.json()["json"])
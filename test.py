import requests

r = requests.get("http://10.255.255.222:88/process_file", json={"filename":["1","22"]})

print(r.text)


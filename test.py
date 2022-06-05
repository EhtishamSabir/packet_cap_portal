import requests

r = requests.post("http://10.255.255.222:88/process_file", json={"files": ["1", "22"]})

print(r.text)

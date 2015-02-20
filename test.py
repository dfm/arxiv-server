import json
from arxiv.oai import download

data = [doc for doc in download(start_date="2015-02-19")]
print(data[0])
print(data[-1])

json.dump(data, open("data.json", "w"), sort_keys=True, indent=4,
          separators=(',', ': '))

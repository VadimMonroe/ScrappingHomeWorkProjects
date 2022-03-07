import requests
import json
from pprint import pprint

# https://api.github.com
# https://api.github.com/users/{academic}/repos{?type,page,per_page,sort}
# https://api.github.com/users/academic/repos

user = 'academic'
url = 'https://api.github.com/users/'

response = requests.get(url + user + '/repos')
j_data = response.json()

with open('json_repo.json', 'w') as f:
    json.dump(j_data, f)

print(f'Список репозиториев юзера:', user)

for i in j_data:
    print(i.get('full_name'))

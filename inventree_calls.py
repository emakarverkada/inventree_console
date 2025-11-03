import requests as re


def get_names(base_url, token):
    head = {"Authorization": token}
    url = base_url + "/api/company/"
    names = []
    try:
        response = re.get(url, headers=head)
        if response.status_code == 200:
            data = response.json()
            for n in data:
                names.append(n["name"])
            return names
        else:
            print("Error:", response.status_code)
            return None
    except re.exceptions.RequestException as e:
        print("Error:", e)
        return None

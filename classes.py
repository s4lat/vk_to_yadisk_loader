import requests as reqs

class VkApi:
    def __init__(self, token: str, v: str):
        self.body = {"access_token": token, "v": v}

    def get_photos_json(self, _id: int, count: int):
        """ 
        Метод получает <count> фотографий со страницы юзера с id = <_id>
        Возвращает tuple:
            tuple[0] - статус завершения, 0 - успешно, 1 - с ошибкой
            tuple[1] - в случае статуса 0 содержит массив словарей для каждой фотографии, 
                иначе строку ошибки

        Словарь каждой фотографии имеет 3 поля: date, likes и url.
        Значение url берется для копии самого большого размера.
        """
        url = "https://api.vk.com/method/photos.get"
        body = {
            "owner_id": _id,
            "album_id": "profile", 
            "count": count, 
            "rev": 1,
            "extended": 1,
            "photo_sizes": 1
        }

        resp = reqs.post(url, data={**body, **self.body}).json()
        if "response" in resp:
            resp = resp["response"]
            photos = self._convert_resp_to_photos(resp)

            return (0, photos)
        else:
            return (1, "[VK] " + resp["error"]["error_msg"])

    def _convert_resp_to_photos(self, resp):
        """
        Отбрасывает ненужные значения response, 
        возвращает массив только с теми данными, которые необходимы
        """
        photos = []
        for item in resp["items"]:
            item = {
                "date": item["date"], 
                "likes": item["likes"]["count"], 
                "url": item["sizes"][-1]["url"],
                "size": item["sizes"][-1]["type"]
            }
            photos.append(item)
        return photos


class YaApi:
    def __init__(self, token: str):
        self.host = 'https://cloud-api.yandex.net:443'
        self.token = token
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }

    def create_folder(self, path: str):
        url = self.host + "/v1/disk/resources"
        resp = reqs.put(url, params={"path": path}, headers=self.headers)
        if resp.status_code == 201:
            return (0, None)
        elif "description" in resp.text:
            return (1, "[YA] " + resp.json()["description"])
        
        return (1, "Unexpected error!")

    def upload_from_url(self, path: str, url: str):
        """
        Метод делает запрос на асинхронную загрузку фотографии с url
        Возвращает два значения:
            1. Статус завершения функции, 0 - успешно, 1 - с ошибкой
            2. Словарь с ссылкой на операцию в яндекс api и путь к файлу в случае успеха, 
                иначе ошибка.
        """
        req_url = self.host + "/v1/disk/resources/upload"
        query = {"path" : path, "url": url}

        resp = reqs.post(req_url, params=query, headers=self.headers, timeout=10).json()
        if "href" in resp:
            return (0, {"href": resp["href"], "path": path})
        elif "error" in resp:
            return (1, "[YA] " + resp["error"])

        return (1, "Unexpected error")

    def get_operation_status(self, url: str):
        resp = reqs.get(url, headers=self.headers)
        return resp.json()

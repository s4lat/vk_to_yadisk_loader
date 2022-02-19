from classes import YaApi, VkApi
from blessings import Terminal
from datetime import datetime
from string import ascii_letters
# from config import *
import requests as reqs
import sys, time, random

STATUS_PADDING = 34

# Counting photo with <n> likes
def count_photos_with_likes(photos: list, likes: int):
     return len([ph for ph in photos if ph["likes"] == likes])

# Generating filenames for photos
def set_filenames(photos: list):
    for i in range(len(photos)):
        if count_photos_with_likes(photos, photos[i]["likes"]) > 1:
            date = datetime.utcfromtimestamp(photos[i]["date"])
            date = date.strftime("%H_%M_%m%d%y")
            photos[i]["filename"] = f"{photos[i]['likes']}_{date}.jpg"
        else:
            photos[i]["filename"] = f"{photos[i]['likes']}.jpg"

def main():
    t = Terminal()
    
    vk_api = VkApi(input("VK_TOKEN: "), "5.131")
    ya_api = YaApi(input("YANDEX_TOKEN: "))
    user_id = int(input("USER_ID: "))
    count = int(input("AMOUNT: "))

    print("Getting photos from VK page...")
    ret, photos = vk_api.get_photos_json(user_id, count)
    if ret:
        print("[ERROR]", photos)
        sys.exit()

    set_filenames(photos)

    # Generating folder uniq name: <user_id>_<hours>_<mins>_<date>_<random seq>
    folder = str(user_id) + "_" + datetime.now().strftime("%H_%M_%d%m%y")
    folder = folder + "_" + "".join([random.choice(ascii_letters) for i in range(4)])
    folder = folder + "/"

    print("Creating folder", folder, "on disk...")
    ret, error = ya_api.create_folder(folder)
    if ret:
        print("[ERROR]", error)
        sys.exit()
    else:
        print("Loading files to folder", folder + ":")

    for i, photo in enumerate(photos):
            ind = f"[{i}]"
            print(f"   {ind:8} {photo['filename']:21} In queue...")

    operations = []
    for i, photo in enumerate(photos):
        path = f"{folder}{photo['filename']}"
        ret, op = ya_api.upload_from_url(path, photo["url"])

        with t.location(x=STATUS_PADDING, y=t.height - len(photos) + i - 1):
            if (ret == 0):
                operations.append(op)
                print("In-progress...")
            else:
                print("[ERROR]", op)

    while len([op for op in operations if "done" not in op]) > 0:
        for i, op in enumerate(operations):
            if "done" in op:
                continue

            status = ya_api.get_operation_status(op["href"])
            with t.location(x=STATUS_PADDING, y=t.height - len(photos) + i - 1):
                if "status" in status:
                    if "suc" in status["status"]:
                        op["done"] = True
                        print("Done!" + " " * 20)
                else:
                    print("[ERROR]", op, + " " * 20)

    print("Done!")

if __name__ == "__main__":
    main()
    sys.exit()
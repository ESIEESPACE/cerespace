import cv2
import requests

from client import client


def take_photo():
    print("Taking photo")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    image = cv2.imencode('.png', frame)[1]
    cam.release()
    upload_photo(image)


def upload_photo(photo):
    url = 'http://{}:8000/photo_upload'.format(client.HTTP_SERVER)
    files = {'photo': photo}
    r = requests.post(url, files=files)
    if r.status_code == 200:
        print("Upload: ok")
        print(r.content.decode("utf-8"))
import cv2


def take_photo():
    print("Taking photo")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    img_name = "photos/opencv_frame_{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    cv2.imwrite(img_name, frame)
    cam.release()
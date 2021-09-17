import cv2
import socket
import multiprocessing as mp
import time

cap = cv2.VideoCapture(2)

HOST = "localhost"
PORT = 7846

otherdata = "hi there"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    cv2.imshow('Input', frame)
    is_success, im_buf_arr = cv2.imencode(".jpg", frame)
    byte_im = im_buf_arr.tobytes()

    c = cv2.waitKey(1)
    if c == 27:
        break
    tosend = str([otherdata, str(byte_im)])
    with open("empty.txt", "w+") as f:
        f.write(tosend)
    s.sendall(tosend.encode("utf-8"))
    time.sleep(2)

cap.release()
cv2.destroyAllWindows()

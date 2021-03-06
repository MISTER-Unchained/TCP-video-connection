import cv2
import socket
import threading as mp
import time

cap = cv2.VideoCapture(1)

HOST = "localhost"
PORT = 7846

seconds_per_frame = 0.2

save_to_file = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
byte_im = None

first_run = True

def read_loop():
    global byte_im
    global first_run
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
        cv2.imshow('Input', frame)
        is_success, im_buf_arr = cv2.imencode(".jpg", frame)
        byte_im = im_buf_arr.tobytes()
        c = cv2.waitKey(1)
        if c == 27:
            break
        if first_run:
            first_run = False



def send_loop():
    global byte_im
    global first_run
    frame_num = 0
    while True:
        if first_run:
            continue
        s.sendall(byte_im)
        time.sleep(seconds_per_frame)
        if save_to_file:
            with open(f"./save/saveIm{frame_num}.jpg", "wb") as f:
                f.write(byte_im)

p1 = mp.Thread(target=read_loop)
p2 = mp.Thread(target=send_loop)
p1.start()
p2.start()
p1.join()
p2.join()

s.close()
cap.release()
cv2.destroyAllWindows()

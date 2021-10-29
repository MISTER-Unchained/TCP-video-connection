import socket
import time
import threading as mp
import cv2
import os
import flask
import copy
import sys

HOST = "192.168.1.108"
PORT = 7846

seconds_per_frame = 0.05

total_data_count = 0
buffer = bytes()
conn = None
addr = None
conn_active = False
global_image = bytes()
frames_processed = 0
times_data_checked = 0

with open("no-conn.jpg", "rb+") as f:
    global_image = f.read()

def check_data_end(data):
    global times_data_checked
    if len(buffer) == 0:
        return False, 0
    ind = data.find(b"\xff\xd9")
    if ind == -1:
        times_data_checked +=1
        return False, 0
    else:
        times_data_checked +=1
        return True, ind - 1

def check_valid_jpg(data):
    if data.find(b"\xff\xd9") == -1:
        return False
    else: return True

def clamp(num, min, max):
    if num >= max:
        return max
    elif num <= min:
        return min
    else:
        return num

def data_analyse():
    global buffer
    current_frame = bytes()
    while True:
        if conn_active == False:
            time.sleep(0.2)
            continue
        data_end, pos = check_data_end(buffer)
        if len(buffer) >= 2_000_000:
            buffer = bytes()
            print("!emptied buffer!")
        if data_end:
            current_frame = buffer[:pos+10]
            buffer = buffer[pos+9:]
            data_handler(conn, addr, current_frame)
        else: 
            time.sleep(seconds_per_frame/2)
        # if len(buffer) > 20000:
        #     print("emtied buffer")
        #     buffer = bytes()


def data_handler(conn, addr, data):
    global global_image
    global frames_processed
    global_image = data
    frames_processed += 1

def socket_loop():
    global total_data_count
    global conn_active
    global buffer
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        print(f"bound to {HOST} @ {PORT}")
        s.listen()
        while True:
            conn, addr = s.accept()
            # todo: make sure nothing runs if there is no connection
            conn_active = True
            with conn:
                print(f"Connected by {addr}")
                while True:
                    rawdata = conn.recv(1024)
                    buffer += rawdata
                    total_data_count += len(str(rawdata))
                    if not rawdata:
                        break
            conn_active = False



def data_log():
    global total_data_count
    global frames_processed
    global times_data_checked
    while True:
        data_count_neat = round(total_data_count/1000)
        print(f"received {data_count_neat} kilobytes/s or {data_count_neat*8} kilobits/s | processed {frames_processed} frames | checked data {times_data_checked} times | current buffersize: {len(buffer)}")
        sys.stdout.write("\033[F")
        total_data_count = 0
        frames_processed = 0
        times_data_checked = 0
        time.sleep(1)

def web():
    global global_image
    dir = os.getcwd()
    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        with open("index.html", "r+") as f:
            index_html = f.read()
        return index_html

    def gen():
        while True:
            time.sleep(seconds_per_frame)
            frame = copy.deepcopy(global_image)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            

    @app.route('/video-feed/')
    def video_feed():
        return flask.Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


    @app.route('/text')
    def text_feed():
        return "succes"

    app.run(host='localhost', debug=False)

socket_loop_process = mp.Thread(target=socket_loop)
socket_loop_process.daemon = True
socket_loop_process.start()

data_log_process = mp.Thread(target=data_log)
data_log_process.daemon = True
data_log_process.start()

data_analyse_thread = mp.Thread(target=data_analyse)
data_analyse_thread.daemon = True
data_analyse_thread.start()

web()

socket_loop_process.join()
data_log_process.join()
data_analyse_thread.join()


cv2.destroyAllWindows()

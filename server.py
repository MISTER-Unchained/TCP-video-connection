import socket
import time
import threading as mp
import cv2
import os
import flask

HOST = "localhost"
PORT = 7846

seconds_per_frame = 0.25

total_data_count = 0
buffer = bytes()
conn = None
addr = None
conn_active = False
global_image = bytes()

with open("no-conn.jpg", "rb+") as f:
    global_image = f.read()

def check_data_end(data):
    for i in range(0, len(data), 1):
        if data[i:i+8] == b"\xff\xd9":
            return True, i
        else: 
            continue
    return False, 0

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
        if data_end:
            print(buffer)
            current_frame = buffer[:pos+10]
            buffer = buffer[pos+9:]
            data_handler(conn, addr, current_frame)


def data_handler(conn, addr, data):
    global global_image
    global_image = data
    with open("check_valid_image.jpg", "wb+") as tempf:
        tempf.write(global_image)

def socket_loop():
    global total_data_count
    global conn_active
    buffer = bytes()
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
    while True:
        data_count_neat = round(total_data_count/1000)
        print(f"received {data_count_neat} kilobytes per second")
        total_data_count = 0
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
            frame = global_image
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

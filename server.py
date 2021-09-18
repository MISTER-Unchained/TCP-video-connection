import socket
import time
import threading as mp
import cv2
import os
import flask

HOST = "localhost"
PORT = 7846

total_data_count = 0

with open("no-conn.jpg", "rb+") as f:
    global_image = f.read()

def check_data_end(data):
    data = str(data)
    if data[-9:] == "\\xff\\xd9'":
        return True
    else: 
        return False


def data_handler(conn, addr, data):
    global global_image
    global_image = data

def socket_loop():
    global total_data_count
    data = bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        print(f"bound to {HOST} @ {PORT}")
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    while True:
                        rawdata = conn.recv(1024)
                        data = data + rawdata
                        if not rawdata:
                            break
                        elif check_data_end(data):
                            break
                    total_data_count += len(str(data))
                    data_handler(conn, addr, data)
                    data = bytes()

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
            time.sleep(0.1)
            frame = global_image
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video-feed/')
    def video_feed():
        with open("client.jpg", "rb+") as f:
            image1 = f.read()
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

web()

socket_loop_process.join()
data_log_process.join()


cv2.destroyAllWindows()

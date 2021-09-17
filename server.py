import socket
import time
import threading as mp

HOST = "localhost"
PORT = 7846

total_data_count = 0

def data_handler(conn, addr, data):
    pass

def socket_loop():
    global total_data_count
    data = ""
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
                        if not rawdata:
                            break
                        decoded_data = rawdata.decode("utf-8")
                        data = data + decoded_data
                        print(len(data))
                    total_data_count += len(data)
                    data_handler(conn, addr, data)
                    data = ""

def data_log():
    global total_data_count
    while True:
        # print(f"received {total_data_count}bytes per second")
        total_data_count = 0
        time.sleep(1)

socket_loop_process = mp.Thread(target=socket_loop)
socket_loop_process.daemon = True
socket_loop_process.start()
data_log_process = mp.Thread(target=data_log)
data_log_process.daemon = True
data_log_process.start()
socket_loop_process.join()
data_log_process.join()

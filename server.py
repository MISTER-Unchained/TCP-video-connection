import socket
import time
import threading as mp

HOST = "localhost"
PORT = 7846

total_data_count = 0


def check_data_end(data):
    if data[-3:] == "END":
        return True
    else: 
        return False

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
                        decoded_data = rawdata.decode("utf-8")
                        data = data + decoded_data
                        if not rawdata:
                            break
                        elif check_data_end(decoded_data):
                            break
                    # Doesn't exit while loop for some reason
                    total_data_count += len(data[:-3])
                    data_handler(conn, addr, data[:-3])
                    data = ""

def data_log():
    global total_data_count
    while True:
        data_count_neat = round(total_data_count/1000)
        print(f"received {data_count_neat} kilobytes per second")
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

import socket

HOST = "localhost"
PORT = 7846

def data_handler(conn, addr, data):
    pass


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    data = ""
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
                    data = data + rawdata.decode("utf-8")
                data_handler(conn, addr, data)
                data = ""
                print(f"{len(data)} bytes received from {addr}")
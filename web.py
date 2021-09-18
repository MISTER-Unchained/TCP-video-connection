import os
import flask
import server

dir = os.getcwd()
app = flask.Flask(__name__)

@app.route('/')
def index():
    with open("index.html", "r+") as f:
        index_html = f.read()
    return index_html

def gen(camera):
    while True:
        frame = camera
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video-feed/')
def video_feed():
    with open("client.jpg", "rb+") as f:
        image1 = f.read()
    return flask.Response(gen(server.global_image), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/text')
def text_feed():
    return "succes"

app.run(host='localhost', debug=False)
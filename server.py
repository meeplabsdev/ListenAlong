from pydeezer import Deezer
from pydeezer.constants import track_formats
from http.server import BaseHTTPRequestHandler, HTTPServer

import socket
import json
import time
import threading

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

start_time  = time.time()

HOST = "127.0.0.1" 
PORT = 36671 # TCP, HTTP is (PORT + 1)
NAME = "Ethan's Music"
PLAYING = False
QUEUE = [
    {"name": "THX", "artist": "CG5", "id": "", "length": 0}, 
    {"name": "Lonely King", "artist": "CG5", "id": "", "length": 0}, 
    {"name": "Noot Noot", "artist": "CG5", "id": "", "length": 0}
]
SONG = QUEUE[0]

playbackSeconds = 0

ARL = config["arl"]
deezer = Deezer(arl=ARL)

def nextSong():
    global start_time
    global playbackSeconds
    global SONG
    global QUEUE

    sin = 0
    tin = 0
    for song in QUEUE:
        if song == SONG:
            tin = sin + 1

            if tin > len(QUEUE) - 1:
                tin = 0

            SONG = QUEUE[tin]
            playbackSeconds = 0
            start_time = time.time() + 5

            return True
        sin += 1
    return False

def hasSongEnded(song, playbackSeconds):
    return int(song["length"]) + 5 <= playbackSeconds

def getSongTime():
    if (PLAYING):
        return playbackSeconds
    else:
        return -2147483647

def getSongInfo():
    if (PLAYING):
        if (SONG["id"] == ""):
            SONG["id"] = deezer.search_tracks(f"{SONG['name']} {SONG['artist']}")[0]["id"]
        if (SONG["length"] == 0):
            track = deezer.get_track(SONG["id"])
            SONG["length"] = track["info"]["DATA"]["DURATION"]
        return {"name": SONG["name"], "artist": SONG["artist"], "id": SONG["id"], "length": SONG["length"], "time": getSongTime()}
    else:
        return {"name": "  ", "artist": "  ", "time": getSongTime()}

def respond(id):
    match id:
        case "reg":
            response_data = {"success": True, "name": NAME}
        case "song":
            response_data = {"success": True, "song": getSongInfo()}
        case _:
            response_data = {"success": False}


    response_json = json.dumps(response_data)
    print(f"Responded: {response_json}")
    return response_json.encode("utf-8")

def respondReq():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}", end="")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f" - Recieved '{data.decode('utf-8')}'")
                    conn.sendall(respond(data.decode("utf-8")))

r_thread = threading.Thread(target=respondReq)
r_thread.daemon = True
r_thread.start()

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(respond((self.path.replace("\\", "/").replace("/", ""))))

def respondReqHttp():
    webServer = HTTPServer(("localhost", PORT + 1), MyServer)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()

rh_thread = threading.Thread(target=respondReqHttp)
rh_thread.daemon = True
rh_thread.start()

def incrementPlaybackSeconds():
    global playbackSeconds
    global start_time

    while True:
        playbackSeconds = time.time() - start_time

p_thread = threading.Thread(target=incrementPlaybackSeconds)
p_thread.daemon = True
p_thread.start()

for T_SONG in QUEUE:
    if (SONG["id"] == ""):
            SONG["id"] = deezer.search_tracks(f"{SONG['name']} {SONG['artist']}")[0]["id"]
    if (SONG["length"] == 0):
        track = deezer.get_track(SONG["id"])
        SONG["length"] = track["info"]["DATA"]["DURATION"]


print("Ready!")
start_time  = time.time()
PLAYING = True

while True:
    if (PLAYING):
        if (hasSongEnded(SONG, playbackSeconds)):
            nextSong()
from tkinter import *
import tkinter as tk
from tkinter.ttk import *
import tkinter.ttk as ttk
from ttkthemes import ThemedTk

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pypresence import Presence
from PIL import Image, ImageTk
from urllib.request import urlopen
from pydeezer import Deezer
from pydeezer.constants import track_formats
from pygame import mixer
from pydub import AudioSegment

import threading
import time
import json
import types
import datetime
import socket
import requests
import numpy as np

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

mode = ""
DEBUG = True

PORT = 36671 # HTTP is 36672
dport = PORT
WIDTH = 200
HEIGHT = 200

ARL = config["arl"]

deezer = Deezer(arl=ARL)
download_dir = os.path.join(os.getcwd(), "output")
mixer.init()
c = mixer.Channel(0)

ui = types.SimpleNamespace()
info = types.SimpleNamespace()

def dprint(string):
    if (DEBUG): __builtins__.print(string)
print = dprint

def center_text(text):
    width = 0
    lines = text.split('\n')
    for line in lines:
        mywidth = len(line)
        if mywidth > width:
            width = mywidth

    centered_lines = [line.center(width) for line in lines]
    centered_text = '\n'.join(centered_lines)
    return centered_text

def startDiscordPresence(info):
    info.line_1 = "  "
    info.elapsed = -2147483647

    d_thread = threading.Thread(target=discordPresence, args=(info,))
    d_thread.daemon = True
    d_thread.start()

def discordPresence(info):
    try:
        client_id = '1139221310065623114'
        RPC = Presence(client_id)
        RPC.connect()

        while True:  # The presence will stay on as long as the program is running
            # state=info.line_2, 
            RPC.update(details=info.line_1, large_image="icon", start=(time.time() - info.elapsed), buttons=[{"label": "Listen Along", "url": "https://github.com/meeplabsdev/listenalong"}])
            time.sleep(15) # Can only update rich presence every 15 seconds
    except:
        pass

def interval_function(function, interval, *args):
    while True:
        function(*args)
        time.sleep(interval / 1000)

def setInterval(function, interval, *args):
    # Create a thread that calls interval_function every 2 seconds
    interval_thread = threading.Thread(target=interval_function, args=(function,interval,*args,))
    interval_thread.daemon = True
    interval_thread.start()

root = ThemedTk()
# root.tk.call('lappend', 'auto_path', './themes')
# root.tk.call('package', 'require', 'awdark')

s = Style()
# s.theme_use('awdark')

root.geometry(f"{WIDTH}x{HEIGHT}")
root.wm_title("Listen Along Player")

background_frame = ttk.Frame(root)
background_frame.place(x=0, y=0, relwidth=1.0, relheight=1.0)

def requestTcp(ip, endpoint, port=00):
    global dport
    if (port == 00):
        port = dport

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))
            s.sendall(endpoint.encode("utf-8"))
            data = s.recv(1024)

        response = json.loads(data)
        if response["success"]:
            dport = port
            return response
        else:
            print(f"Request failed (E_SERVERNOTVALID)")
            print(response)
            return False
    except Exception as e:
        print(f"Request failed with:\n {e}")
        return False

def requestHttp(ip, endpoint, port=00):
    global dport
    if (port == 00):
        port = dport

    try:
        response = requests.get(f"http://{ip}:{port}/{endpoint}", headers={"Bypass-Tunnel-Reminder": "please"})
        response_json = response.json()
        if (response_json["success"]):
            dport = port
            return response_json
        else:
            print(f"Request failed (E_SERVERNOTVALID)")
            print(response_json)
            return False
    except Exception as e:
        print(f"Request failed with:\n {e}")
        return False
    
def request(ip, endpoint, **kwargs):
    global dport
    
    if (mode == "http"):
        return requestHttp(ip, endpoint, **kwargs)
    elif (mode == "tcp"):
        return requestTcp(ip, endpoint, **kwargs)
    else:
        print("NETWORKING DISABLED")
        return False

def secondsToTime(seconds):
    time = str(datetime.timedelta(seconds=int(seconds)))
    return time

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def playSong(id, startSeconds):
    global c

    song = AudioSegment.from_mp3(os.path.join(download_dir, str(id) + ".mp3"))
    song = song[(startSeconds * 1000):]
    song = match_target_amplitude(song, -30.0)

    audio_data = np.array(song.get_array_of_samples())
    s = mixer.Sound(buffer=audio_data.tobytes())

    c.play(s, fade_ms = 250)

def update_ui(ip, ui):
    global c

    response = request(ip, "song")
    if (response == False): return
    response = response["song"]
    name = response["name"]
    artist = response["artist"]
    id = response["id"]
    time = secondsToTime(max(response["time"], 0))

    now_playing_text = center_text(f'{name}\n{artist}\n{time}')
    ui.now_playing.config(text=now_playing_text)

    info.line_1 = f"{name} - {artist}"
    info.elapsed = response["time"]

    if (response and (response["id"] != ui.prev_song_id)):
        ui.prev_song_id = response["id"]
        if (response["id"] > 0):
            c.stop()

            track = deezer.get_track(response["id"])
            if (not os.path.exists(os.path.join(download_dir, str(id) + ".mp3"))):
                track["download"](download_dir, quality=track_formats.MP3_320, with_lyrics=False, with_metadata=True, filename=f"{id}")
        
            ui.now_playing.place(relx=0, rely=0.25, anchor=tk.W)
            cover_url = deezer.get_album(track['info']['DATA']['ALB_ID'])['cover_medium']
            bgimg = ImageTk.PhotoImage(Image.open(requests.get(cover_url, stream=True).raw).resize((min(WIDTH, HEIGHT),min(WIDTH, HEIGHT)), resample=Image.NEAREST))
            ui.background_label.config(image=bgimg)
            ui.background_label.image=bgimg
            ui.background_label.place(x=-2, y=0)
        else:
            c.stop()

            ui.now_playing.place_forget()
            bgimg = ImageTk.PhotoImage(Image.open("icon.png").resize((min(WIDTH, HEIGHT),min(WIDTH, HEIGHT)), resample=Image.NEAREST))
            ui.background_label.config(image=bgimg)
            ui.background_label.image=bgimg
            ui.background_label.place(x=-2, y=0)

    if (not c.get_busy()):
        response = request(ip, "song")
        if (response == False): return
        response = response["song"]
        if (response and (float(response["length"]) > (response["time"] + 6)) and id != 0):
            playSong(f"{id}", max(response["time"], 0))

def setup_ui(ip):
    ui.now_playing = Label(text="\n\n")
    ui.now_playing.place(relx=0, rely=0.25, anchor=tk.W)
    ui.prev_song_id = ""
    setInterval(update_ui, 500, ip, ui)

def connect_to_ip():
    global dport
    global mode

    ip = ui.entry.get()
    ip = ip.replace("https://", "http://")
    if ("http://" in ip):
        mode = "http"
    else:
        mode = "tcp"
    ip = ip.replace("http://", "")

    ui.entry.delete(0, tk.END)
    ui.progress.start()
    ui.progress.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    ui.greeting.place_forget()
    ui.entry.place_forget()

    portsplit = ip.split(":")
    if (len(portsplit) > 1):
        thisport = portsplit.pop()
    else:
        thisport = dport

    ip = ":".join(portsplit)

    if (mode == "http"):
        thisport = int(thisport) + 1
        if(request(ip, "reg", port=thisport) == False):
            thisport = int(thisport) - 1

    print(f"IP:     {ip}")
    print(f"PORT:   {thisport}")

    response = request(ip, "reg", port=thisport)
    if (response != False):
        ui.progress.place_forget()
        ui.state.place(relx=0, rely=0.05, anchor=tk.W)
        ui.state.config(text=f"Connected to {response['name']}!", foreground="lime")

        setup_ui(ip)
    else:
        ui.progress.place_forget()
        ui.greeting.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        ui.entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ui.state.place(relx=0, rely=0.05, anchor=tk.W)
        ui.state.config(text="Connection Failed!", foreground="red")

def on_enter(event):
    connect_to_ip()

bgimg = ImageTk.PhotoImage(Image.open("icon.png").resize((min(WIDTH, HEIGHT),min(WIDTH, HEIGHT)), resample=Image.NEAREST))
ui.background_label = Label(image=bgimg)
ui.background_label.image=bgimg
# ui.background_label.place(x=max((WIDTH-HEIGHT) / 2, 0), y=max((HEIGHT-WIDTH) / 2, 0))
ui.background_label.place(x=-2, y=0)

ui.greeting = Label(text="Enter host IP:")
ui.greeting.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

ui.state = Label()

ui.progress = Progressbar(length=156.75, mode='indeterminate')

ui.entry = Entry(width=25)
ui.entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
ui.entry.bind("<Return>", on_enter)
ui.entry.focus_set()

startDiscordPresence(info)

root.resizable(False, False)
root.attributes('-topmost',True)
root.mainloop()
from pydeezer import Deezer

from serverui import MusicPlayerApp
from serverhoster import Hoster

import json
import time
import threading
import datetime

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

ARL = config["arl"]
deezer = Deezer(arl=ARL)

def timeToSeconds(time_str):
    try:
        # Parse the time string into a timedelta object
        time_delta = datetime.datetime.strptime(time_str, "%H:%M:%S") - datetime.datetime(1900, 1, 1)
        # Convert timedelta to total seconds
        total_seconds = time_delta.total_seconds()
        return total_seconds
    except ValueError:
        raise ValueError("Invalid time format. Use HH:MM:SS")

class Player:
    def __init__(self, name, ui):
        self.name = name
        self.queue = []
        self.song = None
        self.playing = False

        self.start_time = time.time()
        self.playback_seconds = 0

        self.app = ui

        ui.overrideme_play = self.play
        ui.overrideme_stop = self.stop
        ui.overrideme_next = self.next

    def play(self):        
        self.start_time = time.time() + 5
        self.playback_seconds = 0

        self.playing = True
        pass

    def stop(self):
        self.playing = False
        pass

    def next(self):
        self.next_song()
        pass

    def next_song(self):
        sin = 0
        tin = 0
        for song in self.queue:
            if song == self.song:
                tin = sin + 1

                if tin > len(self.queue) - 1:
                    tin = 0

                self.song = self.queue[tin]
                self.playback_seconds = 0
                self.start_time = time.time() + 5

                return True
            sin += 1
        return False

    def has_song_ended(self):
        return int(self.song["length"]) + 5 <= self.playback_seconds

    def get_song_time(self):
        if (self.playing):
            return self.playback_seconds
        else:
            return 0

    def get_song_info(self):
        if (self.playing):
            return {"name": self.song["name"], "artist": self.song["artist"], "id": self.song["id"], "length": self.song["length"], "time": self.get_song_time()}
        else:
            return {"name": "  ", "artist": "  ", "id": 0, "length": 0, "time": self.get_song_time()}

    def respond(self, id):
        self.update_current_playing()

        match id:
            case "reg":
                response_data = {"success": True, "name": self.name}
            case "song":
                response_data = {"success": True, "song": self.get_song_info()}
            case _:
                response_data = {"success": False}

        response_json = json.dumps(response_data)
        print(f"Responded: {response_json}")
        return response_json.encode("utf-8")
    
    def get_queue(self):
        queue = []
        viewqueue = self.app.get_queue()
        for viewitem in viewqueue:
            name = viewitem[0]
            artist = viewitem[1]
            id = viewitem[2]
            duration = timeToSeconds(viewitem[3])

            queue.append({"name": name, "artist": artist, "id": id, "length": duration})
        return queue
    
    def update_current_playing(self):
        self.queue = self.get_queue()
        if (self.playing):
            self.song = self.queue[0]

    def increment_playback_seconds(self):
        self.playback_seconds = time.time() - self.start_time

    def mainloop(self):
        while True:
            self.app.playing = self.playing
            self.queue = self.get_queue()

            if (self.playing and self.song == None):
                if (len(self.queue) > 0):
                    self.song = self.queue[0]
                else:
                    self.playing = False

            self.increment_playback_seconds()
            if (self.playing):
                self.app.update_slider(int(self.playback_seconds), self.song["length"])
                if (self.has_song_ended()):
                    self.app.next_song() # Simulate button press
            
            time.sleep(0.1)

if __name__ == "__main__":
    app = MusicPlayerApp()
    controller = Player("Ethan's Music", app)
    hoster = Hoster(controller.respond)

    mainloop = threading.Thread(target=controller.mainloop)
    mainloop.daemon = True
    mainloop.start()

    app.mainloop()
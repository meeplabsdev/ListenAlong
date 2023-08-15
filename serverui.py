import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

from pydeezer import Deezer

import datetime
import json

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

ARL = config["arl"]
deezer = Deezer(arl=ARL)

def secondsToTime(seconds):
    time = str(datetime.timedelta(seconds=int(seconds)))
    return time

class MusicPlayerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Listen Along Server")
        self.root.resizable(False, False)

        # Create UI elements
        self.song_list = ttk.Treeview(self.root, columns=("Name", "Artist", "ID"))
        self.song_list.heading("#0", text="Name")
        self.song_list.heading("#1", text="Artist")
        self.song_list.heading("#2", text="ID")
        self.song_list.heading("#3", text="Duration")
        self.song_list.bind("<<TreeviewSelect>>", self.ui_update)

        self.add_song_button = ttk.Button(self.root, text="Add Song", command=self.add_song)
        self.remove_song_button = ttk.Button(self.root, text="Remove Song", command=self.remove_song)
        self.play_stop_button = ttk.Button(self.root, text="Play", command=self.play_stop)
        self.next_button = ttk.Button(self.root, text="Next", command=self.next_song)

        self.time_slider = ttk.Scale(self.root, from_=0, to=300, orient="horizontal", length=500, command=self.scrub_slider, state="disabled")
        self.time_current = ttk.Label(text="0:00:00")
        self.time_end = ttk.Label(text="0:05:00")

        self.popup_song = SongNamePopup(self.root)

        # Arrange UI elements
        self.song_list.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.add_song_button.grid(row=1, column=0, padx=10, pady=5)
        self.remove_song_button.grid(row=1, column=1, padx=10, pady=5)
        self.play_stop_button.grid(row=1, column=2, padx=10, pady=5)
        self.next_button.grid(row=1, column=3, padx=10, pady=5)
        self.time_slider.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        self.time_current.grid(row=2, column=0, padx=10)
        self.time_end.grid(row=2, column=3, padx=10)

        # Main variables
        self.playing = False


        self.ui_update()

    def mainloop(self):
        self.root.mainloop()

    # Dynamic functions
    def overrideme_play():
        pass

    def overrideme_stop():
        pass

    def overrideme_next():
        pass

    # Utils

    def add_entry(self, name, artist, id, duration):
        self.song_list.insert("", "end", text=name, values=[artist, id, secondsToTime(duration)])

    def remove_entry(self):
        selected_item = self.song_list.selection()
        if selected_item:
            self.song_list.delete(selected_item)

    def first_item(self):
        items = self.song_list.get_children()
        if items:
            self.song_list.selection_set(items[0])
    
    def get_queue(self):
        resps = []
        children = self.song_list.get_children()
        for child in children:
            try:
                c_child = self.song_list.item(child)
                c_name = c_child['text']
                c_artist = c_child['values'][0]
                c_id = c_child['values'][1]
                c_duration = c_child['values'][2]

                c_resp = [c_name, c_artist, c_id, c_duration]
                resps.append(c_resp)
            except:
                pass
        return resps
    
    def update_slider(self, current_time, finish_time):
        if (current_time > finish_time):
            finish_time = current_time

        if (int(self.time_slider.get()) != int(current_time) or int(self.time_slider.config("to")[4]) != int(finish_time)):
            self.time_slider.config(state="normal")
            if (int(self.time_slider.get()) != int(current_time)):
                self.time_slider.set(int(current_time))
            if (int(self.time_slider.config("to")[4]) != int(finish_time)):
                self.time_slider.config(to=int(finish_time))
            self.time_end.config(text=secondsToTime(finish_time))
            self.time_slider.config(state="disabled")

    # Events

    def scrub_slider(self, value):
        self.time_current.config(text=secondsToTime(float(value)))

        self.ui_update()
        pass

    def add_song(self):
        song = self.popup_song.show_popup()
        if (song != None):
            self.add_entry(song[0], song[1], song[2], song[3])

        self.ui_update()
        pass

    def remove_song(self):
        if (self.song_list.selection() == self.song_list.get_children()[0]):
            self.next_song()
        else:
            self.remove_entry()

        self.ui_update()
        pass

    def play_stop(self):
        self.update_slider(0, 0)
        if (self.playing):
            self.playing = False
            self.overrideme_stop()
        else:
            self.playing = True
            self.overrideme_play()

        self.ui_update()
        pass

    def next_song(self):
        old_select = self.song_list.selection()
        self.first_item()
        self.remove_entry()
        try:
            self.song_list.selection_set(old_select)
        except:
            pass

        self.overrideme_next()

        self.ui_update()
        pass



    # UI Update

    def ui_update(self, *args):
        if (not self.song_list.selection()):
            self.first_item()
        
        self.play_stop_button.config(state="normal")
        if (self.playing):
            self.play_stop_button.config(text="Stop")
        else:
            self.play_stop_button.config(text="Play")

        if (len(self.song_list.get_children()) == 0):
            self.next_button.config(state="disabled")
            if (self.playing):
                self.play_stop_button.config(state="normal")
            else:
                self.play_stop_button.config(state="disabled")
        else:
            if (len(self.song_list.get_children()) > 1):
                self.next_button.config(state="normal")
            else:
                self.next_button.config(state="disabled")
            self.play_stop_button.config(state="normal")

        if (not self.song_list.selection()):
            self.remove_song_button.config(state="disabled")
        else:
            self.remove_song_button.config(state="normal")
        
        if (len(self.song_list.get_children()) == 0 and self.playing):
            self.play_stop()


class SongNamePopup:
    def __init__(self, root):
        self.root = root

    def show_popup(self):
        song_name = sd.askstring("Song Chooser", "Please enter the song name or id:")

        if song_name:
            return self.handle_song(song_name)
        else:
            mb.showinfo("Info", "No song name or id entered.")
            return None

    def handle_song(self, song_name):
        mode = "id"
        try:
            int(song_name)
        except:
            mode = "name"
        
        if (mode == "id"):
            try:
                track = deezer.get_track(song_name)
            except:
                mb.showinfo("Info", "No song found.")
                return None
        else:
            tracks = deezer.search_tracks(song_name, limit=1)
            if (len(tracks) >= 1):
                track = tracks[0]
            else:
                mb.showinfo("Info", "No song found.")
                return None

        name = track['title']
        artist = track['artist']['name']
        identifier = track['id']
        duration = track['duration']
        return [name, artist, identifier, duration]
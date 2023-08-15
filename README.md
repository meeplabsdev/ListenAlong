# ListenAlongPlayer

A python audio player using the deezer API as an alternative to spotify listen along.

## Authors

- [@meeplabsdev](https://www.github.com/meeplabsdev)
  
  ## Usage/Examples
  
  ### From Release
  
  - Download the latest release from Releases.
  
  - Unzip to a folder.
  
  - Make sure you have ffmpeg installed.
  
  - Run setup.exe and login with deezer.
  
  - Run client.exe or server.exe to run the client or server.
  
  ### From Source

Initial setup

Download the zip file of the code and extract it into a folder. Then `cd` into that folder and run:

```cmd
python setup.py
```

You will be asked to login with deezer; A free account will work perfectly fine, however premium accounts will have access to better quality audio.

Installing the dependencies: `cd` into the directory which you extracted the files into and run `pip install -r requirements.txt`.

You must also have ffmpeg installed: [How To Install FFMPEG on Windows 10](https://www.youtube.com/watch?v=r1AtmY-RMyQ)

---

Running the client

```cmd
python client.py
```

A GUI window will appear, in which you must enter the server's IP address. The client will then connect, sync with the server and play the audio.

---

Running the server

```cmd
python server.py
```

The server automatically controls the songs and sends info to connected clients. A simple, intuitive UI gives you the ability to control the songs and queue. Songs can be added by a name search or by their deezer song id. There are two options for connecting:

- HTTP
  
  - Runs on `http://localhost:36672`
  
  - A tunnelling service such as tunnelmole can be used to expose the server to outside clients. 
    
    ```cmd
    tmole 36672
    >>> http://url.here
    >>> https://url.here
    ```
    
    Connect on a client using http://url.here:80
    If you neglect the `:80`, the client will attempt to connect on HTTP http://url.here:36672 and http://url.here:36671.

- TCP
  
  - Runs on `localhost:36671` (no `http://`)
  - Probably quicker
  - Could also tunnel this for outside clients.

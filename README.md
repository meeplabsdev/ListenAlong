# ListenAlongPlayer

A python audio player using the deezer API as an alternative to spotify listen along.

## Authors

- [@meeplabsdev](https://www.github.com/meeplabsdev)
  
  ## Usage/Examples

Initial setup

```cmd
python setup.py
```

You will be asked to login with deezer; A free account will work perfectly fine, however premium accounts will have access to better quality audio.

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

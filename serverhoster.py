from http.server import BaseHTTPRequestHandler, HTTPServer

import socket
import threading
import time

class Hoster:
    def __init__(self, respond):
        self.host = "127.0.0.1" 
        self.port = 36671 # TCP, HTTP is 36672
        self.respond = respond

        r_thread = threading.Thread(target=self.respondReq) # TCP
        r_thread.daemon = True
        r_thread.start()

        rh_thread = threading.Thread(target=self.respondReqHttp) # HTTP
        rh_thread.daemon = True
        rh_thread.start()

        print(f"TCP     {self.host}:{self.port}\nHTTP    http://{self.host}:{self.port + 1}")

    def respondReq(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}", end="")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        # print(f" - Recieved '{data.decode('utf-8')}'")
                        conn.sendall(self.respond(data.decode("utf-8")))

    def respondReqHttp(self):
        webServer = HTTPServer((self.host, self.port + 1), self.HttpServer)
        self.HttpServer.set_respond(self.HttpServer, self.respond)

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()

    class HttpServer(BaseHTTPRequestHandler):
        def set_respond(self, respond):
            self.f_respond = respond

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(self.f_respond((self.path.replace("\\", "/").replace("/", ""))))
import socket
import os

s = socket.socket()
host = socket.gethostname()
port = 12345

s.connect((host, port))
msg = str(s.recv(1024).decode())
while msg != "":
    print(msg)
    try:
        s.send(input("> ").encode())
        msg = str(s.recv(1024).decode())
    except KeyboardInterrupt:
        print("\nTerminating program...")
        break
print("Closing connection with server...")
s.close()

import socket
import threading
import sys

if len(sys.argv) != 3:
  print("usage: client.py <server_ip> <port>")
  sys.exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])

isTalking = False

def recieve(s):
  while True:
    print('recieving')
    data = s.recv(1024)
    print('\n'+data.decode('utf-8'), end='')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
  s.connect((HOST, PORT))
  print("> Server: Enter your name")
  name = input('> ')
  s.sendall(bytes(name, 'utf-8'))

  thread = threading.Thread(target=recieve, args=(s,))
  thread.start()
  user_in = ''
  while user_in != "exit":
    user_in = input('> ').lower()
    s.sendall(bytes(user_in, 'utf-8'))
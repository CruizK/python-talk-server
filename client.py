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
    data = s.recv(1024).decode('utf-8')
    if 'talk request' in data.lower():
      print('\n{0}'.format(data))
    else:
      print(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
  s.connect((HOST, PORT))
  print("> Server: Enter your name")
  name = input('> ')
  s.sendall(bytes(name, 'utf-8'))

  thread = threading.Thread(target=recieve, args=(s,))
  thread.start()
  user_in = ''
  while user_in != "exit":
    if isTalking == True:
      user_in = input('')
    else:
      user_in = input('> ').lower()
    if 'talk' in user_in or 'accept' in user_in:
      isTalking = True
    s.sendall(bytes(user_in, 'utf-8'))
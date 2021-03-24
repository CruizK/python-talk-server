import socket
import threading
import sys

if len(sys.argv) != 3:
  print("usage: client.py <server_ip> <port>")
  sys.exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])

isTalking = False

SERVER_RESP = 1
CHAT_MSG = 2
TALK_REQ = 3
ACCEPT_REQ = 4
TALK_ESTAB = 5
CHAT_DESTROY = 6
CLOSE_CONN = 7

BUFF = 1024

def decode_pkt(pkt):
  pkt = bytearray(pkt)
  msg_type = int.from_bytes(pkt[0:1], byteorder="big")
  msg = pkt[1:].decode('utf-8')
  return (msg_type, msg)

def recieve(s):
  global isTalking
  while True:
    data = s.recv(BUFF)
    pkt = decode_pkt(data)
    if pkt[0] == SERVER_RESP:
      print("Server: {0}".format(pkt[1]), end='\n> ')
    elif pkt[0] == TALK_ESTAB:
      isTalking = True
      print(pkt[1])
    elif pkt[0] == TALK_REQ:
      print(pkt[1], end='\n> ')
    elif pkt[0] == ACCEPT_REQ:
      isTalking = True
      print('')
    elif pkt[0] == CHAT_MSG:
      print(pkt[1])
    elif pkt[0] == CHAT_DESTROY:
      isTalking = False
      print(pkt[1], end='\n> ')
    elif pkt[0] == CLOSE_CONN:
      break
    else:
      break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
  s.connect((HOST, PORT))
  isConnected = True
  print(s.recv(BUFF).decode('utf-8'))
  name = input('> ')
  s.sendall(bytes(name, 'utf-8'))
  thread = threading.Thread(target=recieve, args=(s,))
  thread.start()
  user_in = ''
  while user_in != "exit" or isTalking == True:
    if isTalking == True:
      user_in = input('')
    else:
      user_in = input('> ').lower()
    s.sendall(bytes(user_in, 'utf-8'))
  thread.join()
  

import os
import socket
import subprocess
import threading
import sys

if len(sys.argv) != 2:
  print("usage: server.py <port>")
  sys.exit(1)

HOST = '0.0.0.0'
PORT = int(sys.argv[1])

clients = {}
chats = {}

class Chat:
  def __init__(self):
    self.clients = []

class Client:
  def __init__(self, conn, ip):
    self.talkers = []
    self.ringing = False
    self.conn = conn
    self.ip = ip


def on_client_conn(conn):
  print('Accepted Request from ip: {0}'.format(addr[0]))
  #conn.sendall(b'>Server: Enter your name')
  print('Message Sent Asking For Client-Name')
  name = conn.recv(1024).decode('utf-8').lower()
  clients[name] = Client(conn, addr[0])
  print('{0} named {1}'.format(addr[0], name))
  while clients[name].ringing == False:
    statement = conn.recv(1024).decode('utf-8')
    statement = statement.replace(',', '').split(' ')
    if len(statement) < 2:
      conn.sendall(b'>Server: Invalid Command')
      continue
    cmd = statement[0]
    if cmd == 'talk':
      reciever = statement[1]
      if reciever in clients:
        clients[reciever].conn.sendall(bytes('>Talk Request from {0}@{1}. Respond with "accept {0}@{1}"'.format(name, addr[0]), 'utf-8'))
        chats[name] = Chat()
        chats[name].clients.append(clients[name])
    elif cmd == 'conference':
      pass
    elif cmd == 'accept':
      client_name = statement[1].split('@')[0]
      if client_name in clients and clients[client_name].talkers[0]:
        
    else:
      conn.sendall(b'>Server: Invalid Command')
      continue

      
        
        
        


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  s.listen()
  while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=on_client_conn, args=(conn,))
    thread.start()
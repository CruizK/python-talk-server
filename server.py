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
    self.rung = []

class Client:
  def __init__(self, name, conn, ip):
    self.name = name
    self.talking = False
    self.conn = conn
    self.ip = ip

def chat_thread(my_client, chat):
  print("Starting thread for client {0}".format(my_client.name))
  msg = ''
  while msg.lower() != 'exit':
    msg = my_client.conn.recv(1024).decode('utf-8')
    for client in chat.clients:
      if client != my_client:
        client.conn.sendall('{0}: {1}'.format(client.name, msg).encode('utf-8'))



def on_client_conn(conn):
  print('Accepted Request from ip: {0}'.format(addr[0]))
  #conn.sendall(b'>Server: Enter your name')
  print('Message Sent Asking For Client-Name')
  name = conn.recv(1024).decode('utf-8').lower()
  clients[name] = Client(name, conn, addr[0])
  print('{0} named {1}'.format(addr[0], name))
  while clients[name].talking == False:
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
        chats[name].rung.append(clients[reciever])
        clients[name].talking = True
        conn.sendall('Ringing {0}'.format(reciever).encode('utf-8'))
    elif cmd == 'conference':
      pass
    elif cmd == 'accept':
      client_name = statement[1].split('@')[0]
      chat = chats[client_name]
      if client_name in clients and clients[name] in chat.rung:
        chat.clients.append(clients[name])
        chat.rung.remove(clients[name])
        clients[client_name].conn.sendall('Talk connection established with {0}'.format(name).encode('utf-8'))
        if len(chat.rung) == 0:
          for client in chat.clients:
            client.talking = True
            thread = threading.Thread(target=chat_thread, args=(client,chat,))
            thread.start()
          return
        
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
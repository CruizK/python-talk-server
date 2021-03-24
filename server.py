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


SERVER_RESP = 0
CHAT_MSG = 1
TALK_REQ = 2
ACCEPT_REQ = 3
TALK_ESTAB = 4
CHAT_DESTROY = 5
CLOSE_CONN = 6

BUFF = 1024

clients = {}
chats = {}

class Chat:
  def __init__(self, host):
    self.host = host
    self.clients = []

class Client:
  def __init__(self, name, conn, ip):
    self.name = name
    self.talking = False
    self.ringing = []
    self.conn = conn
    self.ip = ip

def chat_thread(my_client, chat):
  msg = ''
  while msg.lower() != 'exit' and my_client.talking:
    msg = my_client.conn.recv(BUFF).decode('utf-8')
    if chat.host not in chats:
      return
    print('{0}: {1}', my_client.name, msg)
    for client in chat.clients:
      if client != my_client:
        client.conn.sendall(encode_pkt(CHAT_MSG, '{0}: {1}'.format(client.name, msg)))
  
  if chat.host in chats:
    for client in chat.clients:
      client.conn.sendall(encode_pkt(CHAT_DESTROY, 'Connection Terminated'))
      client.talking = False
    del chats[chat.host]


def encode_pkt(msg_type, msg):
  pkt = bytearray()
  pkt.append(msg_type)
  pkt.extend(msg.encode('utf-8'))
  return pkt

def spawn_chat_thread(client, chat):
  thread = threading.Thread(target=chat_thread, args=(client,chat,))
  thread.start()


def on_client_conn(conn):
  print('Accepted Request from ip: {0}'.format(addr[0]))
  conn.sendall(b'>Server: Enter your name')
  print('Message Sent Asking For Client-Name')
  name = conn.recv(BUFF).decode('utf-8').lower()
  clients[name] = Client(name, conn, addr[0])
  print('{0} named {1}'.format(addr[0], name))
  

  while True:
    if clients[name].talking == True:
      pass
    else: 
      rec_line = conn.recv(BUFF).decode('utf-8')
      rec_line = rec_line.replace(',', '').split(' ')

      command = rec_line[0].lower()

      if command == 'exit':
        conn.sendall(encode_pkt(CLOSE_CONN, ''))
        conn.close()
        break
      elif command == 'talk':
        if len(rec_line) < 2:
          conn.sendall(encode_pkt(SERVER_RESP, "talk <client_name>"))
          continue
        reciver = rec_line[1]
        print(reciver)
        if reciver not in clients:
          conn.sendall(encode_pkt(SERVER_RESP, "Invalid Client"))
        else:
          clients[reciver].conn.sendall(encode_pkt(TALK_REQ, 'Talk Request from {0}@{1}. Respond with "accept {0}@{1}"'.format(name, addr[0])))
          conn.sendall(encode_pkt(SERVER_RESP, "Ringing {0}".format(reciver)))
          clients[name].ringing.append(reciver)
          chats[name] = Chat(name)
          chats[name].clients.append(clients[name])
          clients[name].talking = True
          spawn_chat_thread(clients[name], chats[name])
      elif command == 'accept':
        if len(rec_line) < 2:
          conn.sendall(encode_pkt(SERVER_RESP, "accept <client_name>@<client_ip>"))
          continue
        caller_name = rec_line[1].split('@')[0]
        caller = clients[caller_name]
        if caller_name not in clients or name not in caller.ringing:
          conn.sendall(encode_pkt(SERVER_RESP, "Invalid Caller"))
        else:
          caller.ringing.remove(name)
          chat = chats[caller_name]
          chat.clients.append(clients[name])
          caller.conn.sendall(encode_pkt(TALK_ESTAB, "Talk connection established with {0}".format(name)))
          conn.sendall(encode_pkt(ACCEPT_REQ, ''))
          clients[name].talking = True
          spawn_chat_thread(clients[name], chat)
      else:
        conn.sendall(encode_pkt(SERVER_RESP, "Invalid Command"))



"""
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
    """

      
        
        
        


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  s.listen()
  while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=on_client_conn, args=(conn,))
    thread.start()
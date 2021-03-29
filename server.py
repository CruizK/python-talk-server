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



SERVER_RESP = 1
CHAT_MSG = 2
TALK_REQ = 3
ACCEPT_REQ = 4
TALK_ESTAB = 5
CHAT_DESTROY = 6
CLOSE_CONN = 7

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
  msg = my_client.conn.recv(BUFF).decode('utf-8')
  while msg.lower() != 'exit' and my_client.talking:
    
    if chat.host not in chats:
      print("Terminating client", my_client.name)
      my_client.talking = False
      return
    print('{0}: {1}'.format(my_client.name, msg))
    for client in chat.clients:
      if client != my_client:
        client.conn.sendall(encode_pkt(CHAT_MSG, '{0}: {1}'.format(my_client.name, msg)))
    msg = my_client.conn.recv(BUFF).decode('utf-8')
  
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

def start_talk(client, recivers):
  for reciver in recivers:
    clients[reciver].conn.sendall(encode_pkt(TALK_REQ, 'Talk Request from {0}@{1}. Respond with "accept {0}@{1}"'.format(client.name, addr[0])))
    client.conn.sendall(encode_pkt(SERVER_RESP, "Ringing {0}".format(reciver)))
    client.ringing.append(reciver)
  chat = Chat(client.name)
  chat.clients.append(client)
  client.talking = True
  chats[client.name] = chat
  spawn_chat_thread(client, chat)

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
        if reciver not in clients:
          conn.sendall(encode_pkt(SERVER_RESP, "Client {0} is not logged in".format(reciver)))
        elif clients[reciver].talking:
          conn.sendall(encode_pkt(SERVER_RESP, "{0} is in Talk session. Request Dnied".format(reciver)))
        else:
          start_talk(clients[name], [reciver])
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
      elif command == 'conference':
        if len(rec_line) < 4:
          conn.sendall(encode_pkt(SERVER_RESP, "conference talk <client_name1>, <client_name2>"))
          continue
        reciver_one = rec_line[2]
        reciver_two = rec_line[3]
        if reciver_one not in clients or reciver_two not in clients:
          conn.sendall(encode_pkt(SERVER_RESP, "Client {0} is not logged in".format(reciver_one)))
        elif clients[reciver_one].talking or clients[reciver_two].talking:
          conn.sendall(encode_pkt(SERVER_RESP, "{0} is in Talk session. Request Dnied".format(reciver_one)))
        else:
          start_talk(clients[name], [reciver_one, reciver_two])
          clients[name].talking = True
      else:
        conn.sendall(encode_pkt(SERVER_RESP, "Invalid Command"))



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((HOST, PORT))
  s.listen()
  while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=on_client_conn, args=(conn,))
    thread.start()
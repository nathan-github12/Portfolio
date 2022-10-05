
from os.path import join
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json
import sys
import logging


def newConnections():
    #takes in connections from the client and initialies a new thread for the server to handle them on.
    while True:
        client, clientAddress = serverSocket.accept()
        logging.info("%s:%s has connected." % clientAddress)
        Thread(target=currentClient, args=(client,)).start()


def currentClient(client):  
    #takes in the username of the user and checks if its valid.
    name, action, _ = [str(i) for i in client.recv(BUFSIZ).decode("utf8").split('\n')]
    if not validUsername(name):
        client.sendall(("\n".join([str(name), "invalidUsername"])).encode('utf-8'))
        client.close()
    #if it is valid then the user is added to the server and a welcome message is shown.
    elif action == "setName":
        welcomeMessage = 'Welcome %s, type /leave to exit.' % name
        logging.info(welcomeMessage)
        client.sendall(("\n".join([str(welcomeMessage), "message"])).encode('utf-8'))
        joinedMessage = "%s has joined the chat" % name
        logging.info(joinedMessage)
        sendAll(joinedMessage, "")
        clients[client] = name

        sendClients()
    
    #Listens for new messages from the user and executes different functions depending on the action provided
    while True:
        msg, action, recipient = [str(i) for i in client.recv(BUFSIZ).decode('utf-8').split('\n')]
        
        if action == "name":
            changeName(msg, client)
        elif recipient != "All":
            sendRecipient(client,recipient,msg,clients[client]+"->"+recipient+": ")
        elif msg != "/leave":
            sendAll(msg, clients[client]+": ")
        else:
            logging.info("%s has disconnect from the server" % str(clients[client]))
            sendAll(("%s has left the chat." % str(clients[client])), "")
            client.close()
            del clients[client]  
            sendClients()
            break


def sendAll(msg, prefix=""): 
    #sends message to all the users when called
    for client in clients:
        client.sendall(("\n".join([str(prefix + msg), "message"])).encode('utf-8'))
    logging.info(str(prefix + msg))

def sendRecipient(currentClient, rec,msg, prefix=""):
    #sends message to specified user when called
    recipients = []
    recipients.append(currentClient)

    for sock in clients:
        if clients[sock] == rec:
            recipients.append(sock)
    
    for recip in recipients:
        recip.sendall(("\n".join([str(prefix + msg), "message"])).encode('utf-8'))
    logging.info(str(prefix + msg))

def sendClients():
    #sends all the clients currently connected to the server
    clientNames = []
    for client in clients:
        clientNames.append(clients[client])
    clientNames = json.dumps(clientNames)

    for client in clients:
        client.sendall(("\n".join([str(clientNames), "Names"])).encode('utf-8'))


def changeName(clientName, client):
    #changes the name of the user and sends a confimation message
    logging.info("User has changed their name")
    newName = str(clientName)
    clients[client] = newName
    client.sendall(("\n".join(["Username has been changed", "message"])).encode('utf-8'))
    sendClients()

def validUsername(username):
    #checks to see if the username has already been taken
    #if it is taken, an error is shown.
    for client in clients:
        if clients[client] == username:
            logging.error("Invalid Username Entered")
            return False
    return True


#initialises dictionary to store the clients              
clients = {}

#assigsn host, port and buffersize
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
BUFSIZ = 1024
ADDR = (HOST, PORT)

#initialises the server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)

#clears the log file and initialises logging for the server.
with open('server.log', 'w'):
    pass
logging.basicConfig(filename="server.log", level=logging.INFO)

#Initialises the client thread when a new client joins.
if __name__ == "__main__":
    serverSocket.listen(5)
    print("Ready for connection...")
    newClientThread = Thread(target=newConnections)
    newClientThread.start()
    newClientThread.join()
    serverSocket.close()


    

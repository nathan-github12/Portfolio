
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter import StringVar
import json
import sys
from functools import partial


def clientRecieve():
    while True:
        #attempts to recieve a message and an action from the server.
        #if nothing is redcieved then exception is thrown.
        try:
            msg, action = [str(i) for i in clientSocket.recv(BUFSIZ).decode("utf8").split('\n')]
            if action == "Names":
                newMsg = json.loads(msg)
                displayUsers(newMsg)
            elif action == "invalidUsername":
                print("Username is invalid")
                clientSocket.close()
                mainWindow.quit()
            else:
                messageOutput.insert(tkinter.END, msg)
        except: 
            print("You have disconnected from the server")
            clientSocket.close()
            mainWindow.quit()
            break
            


def serverSend(action):  
    #attempts to send message to the server
    #if unable to send then the server has closes so exception is thrown
    try:
        if action == "setName":
            msg = newUsername
        else:
            msg = inputMsg.get()
        recipient = usr.get()
        inputMsg.set("") 
        clientSocket.sendall(("\n".join([str(msg), str(action), str(recipient)])).encode('utf-8'))
        if msg == "/leave":
            clientSocket.close()
            mainWindow.quit()
    except:
        print("Send Connection to server has been lost")
        clientSocket.close()
        mainWindow.quit()
       

def changeName():
    #Called when the change name button is clicked
    #Sends new name to the server
    newName = []
    newName.append(inputMsg.get())
    newName.append("name")
    
    clientSocket.sendall(("\n".join([str(newName[0]), str(newName[1]), "All"]).encode('utf-8')))
    inputMsg.set("")

def displayUsers(users):
    #Puts all the users currently connexted to the server into the Option Menu 
    users.insert(0,"All")
    selectUser['menu'].delete(0,'end')
    for user in users:
        selectUser['menu'].add_command(label = user, command = tkinter._setit(usr, user))
    



#Sets up tkinter interface for the user.

mainWindow = tkinter.Tk()
mainWindow.title = ("Messaging Service")

messageBox = tkinter.Frame(mainWindow)
inputMsg = tkinter.StringVar()  
inputMsg.set("Input Message...")
messageScroll = tkinter.Scrollbar(messageBox)  
messageOutput = tkinter.Listbox(messageBox, height=16, width=55, yscrollcommand=messageScroll.set)
messageScroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
messageOutput.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
messageBox.pack()

messageInput = tkinter.Entry(mainWindow, textvariable=inputMsg)
messageInput.pack(side=tkinter.LEFT)
messageSend = tkinter.Button(mainWindow, text="Send", command= partial(serverSend, "message"))
messageSend.pack(side=tkinter.LEFT)

newNameButton = tkinter.Button(mainWindow, text="Change Name", command = changeName)
newNameButton.pack(side=tkinter.LEFT)


whisperLabel = tkinter.Label(mainWindow, text="Whisper To: ")
whisperLabel.pack(side=tkinter.LEFT)

currentUsers = ["All"]
usr = StringVar(mainWindow)
usr.set(currentUsers[0])
selectUser = tkinter.OptionMenu(mainWindow, usr, *currentUsers)
selectUser.pack(side=tkinter.LEFT)

#Checks to ensure correct amount of arguments have been entered

if len(sys.argv) != 4:
    print('Invalid input - Please follow the form: "python client.py [username] [hostname] [port]"')
    sys.exit(0)

# Assings arguments to relevant variables.

newUsername = sys.argv[1]
HOST = sys.argv[2]
PORT = int(sys.argv[3])

#Assings the buffer size and sets the server address
BUFSIZ = 1024
ADDR = (HOST, PORT)

#attempts to connect to given server address
#if unsuccessful then the server is invalid so the program closes.
try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)
except:
    print("Invalid server address, try again")
    clientSocket.close()
    mainWindow.quit()
    sys.exit()

#sends the username to the server
serverSend("setName") 

#initialises a thread for the current client.
clientThread = Thread(target=clientRecieve)
clientThread.start()
tkinter.mainloop() 

 
import os, tcp_stuff, base64
from threading import Thread
from time import sleep
from functools import partial
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import * #ScrolledText
from tkinter import filedialog


global window, filemenu, theTextArea, isServer, appClosing, theFontSize, theFontName, ipFrame, portEntry, sendEntry, prefixEntry, ipEntry, theButton
window = Tk()
isServer, appClosing = False, False
theFontSize = 9 
theFontName = 'MS Sans Serif' #'courier' #'default' #'fixedsys'
fontSettings = {'font':(theFontName, theFontSize, 'normal'),'foreground':"#00FF00", 'background':'black' }
chButSettings = {'anchor':"w", 'state':"normal", 'height':1, 'pady': 0, 'padx': 0, 'onvalue': True, 'offvalue': False}
serverMode, crSuffix, lfSuffix = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(); lfSuffix.set(True)

# Function used by startGUI to make a program menu bar
def createMenuBar():	
	global menubar, window
	menubar = tk.Menu(window) # Create a menubar to use on the form.
	global filemenu # Create a "File" menu to use in the menubar, and the buttons in the menu
	filemenu = tk.Menu(menubar, tearoff=0)
	filemenu.add_command(label="Save output as..", command=save_as)
	filemenu.add_command(label="Exit", command=on_closing)
	menubar.add_cascade(label="File", menu=filemenu) # Add the file menu to the menubar
	global settingsmenu # Create a menu for "Settings" to place in the menubar (more settings can be added to menu here)
	settingsmenu = tk.Menu(menubar, tearoff=0)
	settingsmenu.add_command(label="Font size +", command=partial( fontsizeChange, True) )
	settingsmenu.add_command(label="Font size -", command=partial( fontsizeChange, False) )
	menubar.add_cascade(label="Settings", menu=settingsmenu) # Add the settings menu to the menubar
	window.config(menu=menubar) # Assign the menubar to the form.

# Function for creating the tkinter graphical user interface
def startGUI():	
	global window, prefixEntry, ipFrame, ipEntry, portEntry, theButton, theTextArea, sendEntry

	window.geometry('800x400+350+70') # Size and location on screen of the form.
	window.title('Python xtelnet') # Set the title of the form
	window.protocol("WM_DELETE_WINDOW", on_closing) # Set what action to take when user click the "x" to close
	
	#Set app icon, using b64 string image
	iconStr = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAECtJREFUWAkBIBDf7wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAMDAwP/AwMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQEBAAAAAAABAQEABAAAAAAQAAAAAAAAAAMDAwACAgH8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAIAAgQAAAAAAgAB/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIEAAAAAAIAAAACAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAB/AIAAgQAAAAAAgACAAAAAwAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/AIAAAAAAAIAAAAAAAH8AAAAAAAAAAAAAAIEAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAgAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfwCAAAAAgACAAIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAfwCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAIAAAAAAAAAAAACAAAAAAAAAAAAAfwAAAH8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAB/AIAAAAAAAAAAAAAAAAAAAACAAIAAAACAAIAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAH8AgAAAAAAAAAAAAAAAgQAAAIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAgAAAAAAAAAAAAAAAAACBAIAAAAAAAAAAAACAAIAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgQCAAAAAAAB/AIAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAH8AAAAAAAAAAAAAAIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAgACBAAAAAACAAAAAgAB/AIEAgAAAAAAAfwCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgQAAAAAAgAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAEBAQACAgIEAgAAAAAAAAAAAAAAAAACBAAAAgAAAAAAAAAAAAIAAgACAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAIAAfwCAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAABAQEAAAAAAAAAAAAAAAAAAAAAAAAAAgACBAAAAAAAAAH8AAAAAAAAAAAAAAAAAAACAAAAAgAAAAAAAgAB/AAAAAAAAAAAAAACBAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAIAAAAAAAAAAAAAAAIAAgAAAAIAAAAAAAAAAAACAAH8AAAAAAAAAAAAAAIEAgACAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAAB/AAAAfwCAAAAAAAB/AIAAfwAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAgAAAAAAAAAAAAAAAAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAgQAAAIEAAAAAAAAAAAAAAH8AgAAAAAAAAAAAAAAAAACBAAAAgQAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAAAAfwAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAIAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAIAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAIEAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAACAAAAAAAAAAIAAAACAAAAAgACAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAIAAAAAAAIAAAAAAAIAAAAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAACAAAAAAAAAAAAAAACAAAAAAAAAAAAAgAB/AAAAAAAAAAAAAAAAAAAAAAAAAH8AgACBAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAADAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAH8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/AAAAfwAAAAAAgACAgAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAgACAAIAAAAB/AAAAAAAAAAAAAAAAAAAAAAAAAIEAgAAAAAAAAACAAH8AAAAAAAAAAAAAAH8AAACBAAAAAACAAAAAAAAAAIAAgAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAACBAAAAgQAAAAAAAACAAIAAAAAAAIEAgAAAAAAAAAAAAAAAAAB/gIAAAAAAAAAAAAAAAAAAgAAAAIAAgAAAAAAAwMDAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAH8AAAAAAAAAAAAAAIEAAAAAAAAAAACAAIAAgAAAAAAAAACAAAAAAACBAAAAAAAAAAAAAAAAAAAAfwAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAB/AAAAfwAAAAAAAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAAAAACAAAAAAIAAAACAAAAAAAAAgQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAIEAAAAAAAAAfwAAAH8AAAAAAIAAAAAAAAAAAACAAAAAAAAAAMDAwAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAIEAAAAAAAAAgACAAIAAgAAAAIAAAACAAAAAgAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgQAAAAAAAAB/AAAAfwAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAACAAIAAAAAAAAAAAACAAAAAAAAAAACAAAAAAIAAAAAAAAAAgAAAAIAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAACAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAMDAwP8AAAAAwMDAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAACAAAAAAIAAAACAAAAAAAAAAIAAAAAAAAAAgIAAAACAAAAAAAAAAIAAAAAAAAAAgAAAAAAAAACAAAAAAAAAgIAAAAAAAAAAAACAgIABAAAAAAEAAAAAAAAAAMDAwP8AAAAAAAAAAMDAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAQADAwMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAQABAQEABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPhsMWlxra2AAAAAElFTkSuQmCC'
	appIcon = tk.PhotoImage(master=window, data=iconStr)#appIcon = tk.PhotoImage(master=window, file="x.png")
	window.tk.call('wm', 'iconphoto', window._w, appIcon)
	createMenuBar()
	
	#Configure style for the text entries
	ttk.Style().configure('my.TEntry', padding='1 3 0 0', fieldbackground='black', selectbackground='white', selectforeground='black', insertbackground='white', insertcolor='white' )
	
	#Create a frame that contains ALL other frames
	mainFrame = tk.Frame(window) 
	mainFrame.pack(fill='both', expand=True)
	
	#Dividing the space in the mainFrame into 3 horizontal frames (380px remains after file menubar is set) 
	topFrame = tk.Frame(mainFrame, height=30)
	middleFrame = tk.Frame(mainFrame, height= 300 )
	bottomFrame = tk.Frame(mainFrame, height=50)
	
	topFrame.pack(fill=tk.X)
	middleFrame.pack(expand=True, fill='both')
	middleFrame.pack_propagate(0) #Important, keeps middleFrame from taking all space left?
	bottomFrame.pack(fill=tk.X) 
	
	
	#Divide topFrame into two frames side by side, leftFrame and rightFrame
	#leftFrame will contain the prefixEntry, rightFrame will contain ip, port, buttons floating right
	leftFrame = tk.Frame(master=topFrame, width=100)
	leftFrame.pack(fill=tk.X, side=tk.LEFT, padx=5, expand=True) #prefixFrame and prefixEntry must expand too	
	rightFrame = tk.Frame(master=topFrame)
	rightFrame.pack(fill=tk.X, side=tk.RIGHT, padx=1)	

	
	#Set contents of leftFrame:
	prefixFrame = tk.Frame(master=leftFrame, height=100, width=100)
	prefixFrame.pack(fill=tk.X, side=tk.LEFT, padx=2, expand=True)
	
	#prefixFrame has a LABEL above and ENTRY below
	prefixLbl = Label(prefixFrame, text = "Prefix", anchor=W)
	prefixLbl.pack(side=TOP, anchor=NW)#side=tk.LEFT)
	
	
	prefixEntry = ttk.Entry(prefixFrame, style='my.TEntry') 
	prefixEntry.configure(fontSettings)
	prefixEntry.pack(fill=tk.X, expand=True, ipady=1)
	#And that's all for leftFrame, done with it
	
	
	#Divide rightFrame into 3 separate frames:
	ipFrame = tk.Frame(master=rightFrame) #ipFrame is global for hide/show according to mode( server or client )
	portFrame = tk.Frame(master=rightFrame)
	btnFrame = tk.Frame(master=rightFrame)
	#These frames MUST be packed in correct order because tk.RIGHT
	btnFrame.pack(fill=tk.X, side=tk.RIGHT, padx=1)
	portFrame.pack(fill=tk.X, side=tk.RIGHT, padx=5)
	ipFrame.pack(fill=tk.X, side=tk.RIGHT, padx=5)
	
	
	#Set contents of ipFrame: a LABEL above and ENTRY below
	ipLbl = Label(ipFrame, text = "IP")
	ipLbl.pack(side=TOP, anchor=NW)
	
	ipEntry = ttk.Entry(ipFrame, width=15, style='my.TEntry')
	ipEntry.configure(fontSettings)
	ipEntry.pack(ipady=1); ipEntry.insert(0, "127.0.0.1")
	
	
	#Set contents of portFrame: a LABEL above and ENTRY below
	portLbl = Label(portFrame, text = "Port")
	portLbl.pack(side=TOP, anchor=NW)
	
	portEntry = ttk.Entry(portFrame, width=5, style='my.TEntry')
	portEntry.configure(fontSettings)
	portEntry.pack(ipady=1); portEntry.insert(0, "8080")
	
	
	#Set contents of btnFrame: a Checkbutton above and Button below
	srvCheckBtn = Checkbutton(btnFrame,
					text='TCP Server',
					command=srvCheckbutton_changed,
					variable=serverMode,
			 		width = 10)
	srvCheckBtn.configure(chButSettings)
	srvCheckBtn.pack()
	
	imgVar = tk.PhotoImage(width=1, height=1)
	
	theButton = Button(btnFrame, 
				   image=imgVar, 
				   text="Connect", 
				   command=btnAction, width=80, height=10, 
				   compound = CENTER )
	theButton.pack()
	#Done with the rightFrame contents
	
	
	#Set contents of middleFrame: a textarea for showing output
	theTextArea = ScrolledText(middleFrame)# Create a textarea 
	theTextArea.configure( selectbackground='white', selectforeground='black', insertbackground='white' )
	theTextArea.configure(fontSettings)
	theTextArea.pack(expand=1, fill='both', padx=5, ipadx=5, ipady=5) # Place the textarea onto the form.
	
	
	#Divide bottomFrame into one frame for text input (Entry) and one frame for suffix (Checkbuttons cr lf )
	sendFrame = tk.Frame(master=bottomFrame, width=10, height=50)
	sendFrame.pack(fill=tk.X, side=tk.LEFT, padx=5, expand=True)
	suffixFrame = tk.Frame(master=bottomFrame, width=3, height=50)
	suffixFrame.pack(fill=tk.X, side=tk.RIGHT)		
	
	
	#Set contents of sendFrame: Entry for text input to send
	sendEntry = ttk.Entry(sendFrame, style='my.TEntry')
	sendEntry.configure(fontSettings)
	sendEntry.pack(pady=5, fill=tk.X, expand=True, ipady=1)
	sendEntry.bind('<Return>', sendUserInput)
	
	
	#Set contents of suffixFrame: Checkbuttons for adding suffixes cr(\r) and/or lf(\n) to the sendstring
	crCheckBtn = Checkbutton(suffixFrame,
					text='\\r',
					variable=crSuffix,
			 		width = 2)
	crCheckBtn.configure(chButSettings)
	crCheckBtn.pack(ipady=0)

	lfCheckBtn = Checkbutton(suffixFrame,
					text='\\n',
					variable=lfSuffix,
			 		width = 2)
	lfCheckBtn.configure(chButSettings)
	lfCheckBtn.pack(ipady=0)
	
	# Gui should be ready, we can read incoming
	Thread(target=processIncoming).start()
	window.mainloop()  # Execute window main event handler


# Function to initiate client connection when in client mode
def startClient():	
	buttonEnabled(False)
	global theButton, portEntry, ipEntry
	ip = ipEntry.get() #Get ip from Entry
	port = int( portEntry.get() ) #Get port and convert to int
	Thread(target=tcp_stuff.clientConnect , args=(ip, port,) ).start()
	Thread(target=clientStartReading).start()

# Function for client mode to verify connection and start process data from socket 
def clientStartReading():	
	global theButton
	errorMsg = "none"
	i = 0
	while True:
		sleep(0.5)
		if tcp_stuff.running:
			addText("%s *** TCP connection established."%(tcp_stuff.timeStamp() ))
			#Thread(target=processIncoming).start()	#start processessing incoming data
			theButton.config(text = "Disconnect")
			break
		i+=1
		if i == 10: # 5 sec
			if(len(tcp_stuff.errorArr) > 0):
				errorMsg = tcp_stuff.errorArr.pop(0)
			addText("%s *** TCP connection failed! (%s) "%(tcp_stuff.timeStamp(), errorMsg))
			break
	buttonEnabled(True)

# Function for client mode to shut down socket connection
def stopClient():	
	buttonEnabled(False)
	global theButton
	try:
		theButton.config(text = "Connect")
	except Exception as e:
		pass

	try:
		sock = tcp_stuff.sockArr[0]
		sock.shutdown(1)
		sock.close()
	except Exception as e:
		pass
	tcp_stuff.running = False
	buttonEnabled(True)



# Function to initiate server listening when in server mode
def startServer():	
	global portEntry#, theButton
	buttonEnabled(False)
	port = portEntry.get() #Get port from Entry
	tcp_stuff.listenPort = int( port )
	addText("%s *** TCP Server (%d) initiating.."%(tcp_stuff.timeStamp(), tcp_stuff.listenPort))
	Thread(target=tcp_stuff.portListener).start()	#Starts the server portListener
	Thread(target=serverStartReading).start()

# Function for server mode to verify listening and start processing data from socket connections
def serverStartReading():
	global theButton
	i = 0
	while True:
		sleep(0.5)
		if tcp_stuff.running:
			addText("%s *** TCP Server (%d) started"%(tcp_stuff.timeStamp(), tcp_stuff.listenPort))
			#Thread(target=processIncoming).start()	#start processessing incoming data
			theButton.config(text = "Stop")
			break
		i+=1
		if i == 6: # 3 sec
			if(len(tcp_stuff.errorArr) > 0):
				errorMsg = tcp_stuff.errorArr.pop(0)
			addText("%s *** TCP Server (%d) failed! (%s) "%(tcp_stuff.timeStamp(), tcp_stuff.listenPort, errorMsg))
			break	
	buttonEnabled(True)

# Function for server mode to shut down socket connections and stop listener 
def stopServer():	
	buttonEnabled(False)
	global theButton
	theButton.config(text = "Start")
	tcp_stuff.running = False
	tcp_stuff.killListener()#make sure listener also closes
	addText("%s *** TCP Server (%d) stopped"%(tcp_stuff.timeStamp(), tcp_stuff.listenPort))
	buttonEnabled(True)



# Function for both server and client mode, takes care of incoming data
def processIncoming():	
	global appClosing #isServer
	sleep(0.5)
	while True:
		sleep(0.1)
		if(len(tcp_stuff.inputArr) > 0):
			incoming = tcp_stuff.inputArr.pop(0)
			addText(incoming)
		if appClosing: #if not tcp_stuff.running:
			break
	
	if(isServer):
		tcp_stuff.killListener()#make sure listener also gets to close
	else:
		stopClient()
	#addText("Debuginfo: processIncoming closing..")

# Function triggered by enter key in sendEntry, tries to send to current socket
def sendUserInput(event):	
	global prefixEntry, sendEntry
	try:
		if len( tcp_stuff.sockArr ) == 1:
			prefixStr = prefixEntry.get()
			addCR = crSuffix.get()
			addLF = lfSuffix.get()
			suffixStr = ""
			if(addCR):
				suffixStr += '\r'
			if(addLF):
				suffixStr += '\n'
			sendText = sendEntry.get()
			sendText = sendText.rstrip() #in case there is any \r or \n 
			tcp_stuff.sockArr[0].send( str.encode(prefixStr + sendText + suffixStr) )
			addText(prefixStr + sendText) #addText will add \n
			sendEntry.delete(0, tk.END)
	except Exception as e:
		addText("Debuginfo: " + str(e) )

# Function triggered by button, start/stop server when server mode or connect/disconnect client when client mode
def btnAction():	
	global isServer
	if(isServer):
		if not tcp_stuff.running:
			startServer()
		else:
			stopServer()
	else:
		if not tcp_stuff.running:
			startClient()
		else:
			stopClient()

# Function for toggling the button state DISABLED/NORMAL
def buttonEnabled(enabled):
	# Declare toggler function to be executed in separate thread
	def buttonToggler(enabled):
		global theButton
		try:
			if enabled:
				sleep(1); theButton.config(state=NORMAL); return
			theButton.config(state=DISABLED)
		except Exception as e:
			pass
	# Do the toggling in separate thread
	Thread(target=buttonToggler, args=(enabled,) ).start()

# Function triggered by checkbutton change, toggle GUI mode client/server
def srvCheckbutton_changed():	
	global theButton, window, ipFrame, isServer
	try:
		isServer = serverMode.get()
		if(isServer):
			ipFrame.pack_forget()
			window.title('Python xtelnet [server mode]')
			theButton.config(text = "Start")
		else:
			if tcp_stuff.running:
				stopServer()
			ipFrame.pack()
			window.title('Python xtelnet')
			theButton.config(text = "Connect")
	except Exception as e:
		pass

# Function to append text to textArea
def addText(inputStr):	
	global theTextArea
	try:
		theTextArea.insert(tk.END, inputStr + "\n")
		theTextArea.see(tk.END)
	except Exception as e:
		pass

# Function for showing msgBox with input
def showMsgBox(inputStr):	
	messagebox.showinfo(title='Result', message = inputStr)

# Function triggered when user tries to close the form.
def on_closing():	
	global isServer, appClosing
	if messagebox.askokcancel("Quit", "Do you want to quit?"): # if user clicks yes, we exit, if cancel, we do nothing, form stays open
		appClosing = True
		tcp_stuff.running = False #Should cause any open threads with sockets to close up
		exit(0) 

# Function to increase/decrease font size in textArea
def fontsizeChange(incr):	
	global theFontSize, theTextArea
	if incr:
		theFontSize += 1
	else:
		theFontSize -= 1
	theTextArea.configure( font = (theFontName, theFontSize, 'normal')    )

# Function to save the text output to file, prompts user to set file name
def save_as():	
	f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
	if f is None: # return `None` if dialog closed with "cancel".
		return # we dont continue if the user cancels
	try:
		saveFile = os.path.abspath(f.name) # Get the absolute path to the file
		saveTxt = theTextArea.get(1.0, END).encode('utf-8') # Fetch the text from textarea
		f = open(saveFile, "w")
		f.write( saveTxt.decode('utf-8') ) # Write the text to file
		f.close()
		showMsgBox(f.name + " SAVED!") # Brag about how successfully it was saved!
	except Exception as e:
		showMsgBox( str(e) ) # Or not..
		pass

if __name__ == "__main__":
	startGUI() # Opens the tk form/window/GUI
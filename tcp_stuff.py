import socket, sys
from threading import Thread
from time import sleep, strftime
from datetime import datetime

BUFLEN = 1024
global inputArr, errorArr, running, listenPort, sockArr
listenPort = 8080
inputArr, errorArr, sockArr = [], [], []
running = False
debugging = True

############################# SHARED FUNCTIONS FOR BOTH CLIENT AND SERVER MODE GOES HERE ##################################

# Function to print debug info to terminal console (when debugging = True)
def debug(inputStr):	
	if debugging:
		print(inputStr)

# Function to remove used socks, must be above the others
def cleanups(theSocket):	
	global sockArr
	try:
		sockArr.remove(theSocket)
	except Exception as e:
		pass
		
	try:
		theSocket.shutdown(1)
		theSocket.close()
	except Exception as e:
		pass


############################# FUNCTIONS FOR CLIENT MODE GOES HERE #########################################################

# Function for client mode, connect and read socket
def clientConnect(ip, port):	
	global running, listenPort, stopClient, errorArr
	try:
		theSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		theSocket.connect((ip, port)) #open a new socket
		sockArr.append(theSocket)
	except Exception as e:
		errorArr.append( str(e) )
		debug("Unable to connect?")
		return

	running = True
	try:
		#debug(theSocket)
		host, localport = theSocket.getsockname()
		appendData(timeStamp() + " *** Connected ("+ ip +":"+ str(port) +") ("+str( localport )+")")
		socket_buffer = ''
		while 1:
			if not running:
				debug("clientConnect is shutting down!")
				break
			sleep(0.20) #IMPORTANT SLEEP HERE, NO REMOVEY :S
			
			buff = theSocket.recv(BUFLEN)
			if not buff: #the socket closed, normal and expected behaviour
				appendData(timeStamp() + " *** Disconnected ("+ ip +":"+ str(port) +") ("+str(localport)+")")
				running = False
				break 
			if( len(buff) > 0 ):
				socket_buffer += buff.decode("utf-8") #append data to socket_buffer
				end = socket_buffer.find('\n')#ending with newline char
				if end!=-1: #if buffer end is \n we process it
					socket_buffer = socket_buffer.rstrip()
					inputArr.append(socket_buffer)
					#debug("'" + socket_buffer + "'")
					socket_buffer = '' #reset the buffer now, and keep reading
		cleanups(theSocket)#close it up when finished

		
	except Exception as e:
		#debug("Whoopsie!"); debug('Error on line {} in "clientConnect": '.format(sys.exc_info()[-1].tb_lineno) + " '" + str(e) + "'")		
		cleanups(theSocket)
		if (str(e) == "timed out") and ( running ):
			appendData(timeStamp() + " *** Disconnected ("+ ip +":"+ str(port) +") ("+str(localport)+") (timed out)")
		if (str(e) != "timed out") and ( running ):
			debug('Error on line {} in "clientConnect": '.format(sys.exc_info()[-1].tb_lineno) + " '" + str(e) + "'"); pass


############################# FUNCTIONS FOR SERVER MODE GOES HERE #########################################################

# Dirty workaround to kill listener when closing and listener loop is blocking 
def killListener():		
	# define function to be opened in separate thread
	def _sendDie(sendString):
		global running, listenPort
		try:
			newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			newSock.connect(("127.0.0.1", listenPort)) #open a new socket
			newSock.settimeout(2)# If not, and you send a command without tray app being up, the GAME will hang while waiting for default timeout
			newSock.send(str.encode(sendString + "\n") )#send the data
			cleanups(newSock)#remove nasty dirty socks when done
			debug("killListener successfully executed")
		except Exception as e:
			cleanups(newSock)
			if (str(e) != "timed out") and ( running != False):
				debug('Error on line {} in "_sendData": '.format(sys.exc_info()[-1].tb_lineno) + " '" + str(e) + "'"); pass
	Thread(target=_sendDie, args=("die",) ).start()


# Function for "portListener", must be placed above listener function
def getData(connection, address, timeout):	
	global inputArr, running, listenPort, sockArr
	theSocket = connection
	sockArr.append(theSocket)
	try:
		theSocket.settimeout(timeout)
		ip = str(address[0])
		port = str(address[1])
	except Exception as e:
		cleanups(theSocket)
		return
	
	if not running:
		cleanups(theSocket)
		return
	try:
		appendData(timeStamp() + " *** Client ("+ ip +":"+ port +") connected ("+str(listenPort)+")")
		socket_buffer = ''
		while 1:
			if not running:
				#debug("getData is shutting down!")
				break
			sleep(0.20) #IMPORTANT SLEEP HERE, NO REMOVEY :S
			
			buff = theSocket.recv(BUFLEN)
			if not buff: #the socket closed, normal and expected behaviour
				#debug("client closed socket") #debugging
				appendData(timeStamp() + " *** Client ("+ ip +":"+ port +") disconnected ("+str(listenPort)+")")
				break 
			if( len(buff) > 0 ):
				socket_buffer += buff.decode("utf-8") #append data to socket_buffer
				end = socket_buffer.find('\n')#ending with newline char
				if end!=-1: #if buffer end is \n we process it
					socket_buffer = socket_buffer.rstrip()
					inputArr.append(socket_buffer)
					#debug("'" + socket_buffer + "'")
					socket_buffer = '' #reset the buffer now, and keep reading
		cleanups(theSocket)#close it up when finished

		
	except Exception as e:
		#debug("Whoopsie!") #debug('Error on line {} in "getData": '.format(sys.exc_info()[-1].tb_lineno) + " '" + str(e) + "'")		
		cleanups(theSocket)
		if (str(e) == "timed out") and ( running ):
			appendData(timeStamp() + " *** Client ("+ ip +":"+ port +") disconnected ("+str(listenPort)+") (timed out)")
		if (str(e) != "timed out") and ( running ):
			debug('Error on line {} in "getData": '.format(sys.exc_info()[-1].tb_lineno) + " '" + str(e) + "'"); pass


# Function for appending data to array so that GUI can add it to textArea
def appendData(inputStr):	
	global inputArr
	inputArr.append(inputStr)


# Function for returning a nice formatted timestamp
def timeStamp():	
	return datetime.now().strftime('%H:%M:%S')	


# Function to listen for connections
def portListener(host='0.0.0.0', timeout=300, handler=getData):		
	global running, listenPort, sockArr, errorArr
	try:
		soc_type=socket.AF_INET
		soc = socket.socket(soc_type)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		soc.bind((host, listenPort))
		soc.listen(0)
	except Exception as e:
		errorArr.append( str(e) )
		debug("Error: " + str(e) )
		return

	running = True
	while 1:
		try:
			newSock, newAdd = soc.accept()
			if len(sockArr) == 0:
				Thread(target=handler, args=(newSock, newAdd, timeout,)  ).start()
			else:
				rejected, rejAddr = soc.accept()
				rejected.shutdown(1)
				rejected.close()
				appendData(timeStamp() + " *** Client ("+ str(rejAddr[0]) +":"+ str(rejAddr[1]) +") rejected ("+str(listenPort)+")")
			if not running:
				debug("Listener shutting down now..")
				break
		except Exception as e:
			debug("Error: " + str(e))
			pass
	soc.shutdown(1); soc.close()
	for client in sockArr: #Expect max 1
		cleanups(client)
	debug("Listener closed!")
# xtelnetPy
Socket client/server debugging app with tkinter GUI 

Nothing fancy, it is just a python script with GUI, able to act as a server or a client for data transfer.

A python replication I made of a tiny old windows program called "xtelnet.exe", which I've used over the years 
for quickly debugging all sorts of tcp socket connections and their protocols. Useful for reverse engineering
old server/client software when porting to new or when making new compatible software.

If you examine a server software and you need to figure out how its protocol works, you can use xtelnet to connect
to the server and see the output of what it sends, and you can type in what to send to test how server responds.
Vice versa, if you have some client software you need to examine, you can set up xtelnet as a server
and have the client software connect to it so you can see what it outputs and test responses.

Server takes only one client at a time, it will reject new connection attempt if already busy.
Customizable prefix on sending string, and can be set to use suffix CR and/or LF on sending.
The GUI has settings for increasing or decreasing font size, and for saving output to file.

In addition, xtelnet can also be used as a pure cleartext tcp "chat" between two parties where one acts 
as server and the other client, if both set their nickname as prefix the result will look chatt'ish. 

<b>How to run?</b>
Open terminal and type:

python xtelnet.py

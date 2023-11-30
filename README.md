# Distributed-File-Transfer-P2P
Assignment 2 of the course Computer Networks at IIT Delhi Sem 1 23-24

Our team implemented a p2p exchange network through **master client** and **slave clients**.
Each of the clients is connects to thes server to read the lines in txt file. Information exchange
occurs separately for each master and slave client pair. The master client acts as a central hub for receiving and sending the data for all the clients

###Slave Client :

The slave client runs three parallel threads -
1. reading from vayu
2. reading from the master client
3. sending to the master client.

Each slave client maintains its own dictionary to store the lines. Whenever a new line is added to the dictionary, that line is sent to the master client. Parallely, it also receives from the master client and adds the received line to its dictionary if it’s a new line. We implemented a two-way communication via receiving and sending thread for master-slave. 

###Master Client :

The Master client runs two parallel threads for sending and receiving from each slave i.e. 6 parallel threads and one separate thread for reading from server. We maintained three separate queues for sending to each of the slave clients. Whenever a new line received from a certain slave is added in the dictionary, the same line is added to the queues of the remaining two slave clients and popped accordingly. The termination condition is when the master client has received all 1000 lines and all the queues of slave clients are empty i.e it has sent everything new it had. A new line detection is always occurring at the receiver’s end.

In this way, all the information is being shared among all the peers with a central authority to manage distribution.

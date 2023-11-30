import socket
import threading
import queue
import time

rec_server_address = ('10.194.19.137', 13730) #ip address and ports of master for receiving
send_server_address = ('10.194.19.137', 13732) #ip address and ports of master for sending
recv_from_mainerver = ('10.17.51.115',9801) #vayu

rec_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv_from_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

rec_socket.bind(rec_server_address)
send_socket.bind(send_server_address)

rec_socket.listen(3)
print("Server is listening for incoming connections (receiving)...")

send_socket.listen(3)
print("Server is listening for incoming connections (sending)...")

global lines
lines = {}


line_lock = threading.Lock()

recv_from_main.connect(recv_from_mainerver)
#list of ip address of slave clients
client_ip = ['10.194.3.154', '10.194.38.13', '10.194.34.30']
dict_queues = {}
for i in client_ip:
    dict_queues[i] = queue.Queue()

def final_checker():
    ans="SUBMIT\n"
    ans+="2020CS10404@pirate\n" + "1000\n"
    recv_from_main.send(ans.encode('utf-8'))
    for i in range(1000):
        message = str(i)+"\n" +lines[i] + "\n"
        recv_from_main.send(message.encode('utf-8'))
    data = recv_from_main.recv(4096)
    print("kuch aya")
    print("Received data:", data.decode('utf-8'))  
    message = "SEND INCORRECT LINES\n"
    recv_from_main.send(message.encode('utf-8'))
    data2 = recv_from_main.recv(4096)
    data2_dec = data2.decode('utf-8')
    print(data2_dec)
    recv_from_main.close()
    print("Closed socket")

def recv_mainserver():
    while True:
        prev_response = ""
        print("server connected to vayu")
        try:
            while True:
                with line_lock:
                    if len(lines) >= 1000:
                        print("all lines rec", time.time() - start_time)
                        return final_checker()
                message = "SENDLINE\n"
                recv_from_main.sendall(message.encode('utf-8'))
                data_main = recv_from_main.recv(4096)
                data_main_decode = data_main.decode('utf-8')
                if data_main_decode=='-1\n\n'  or data_main_decode == '-1\n':
                    continue
                elif data_main_decode.endswith('\n'):
                    data_main_decode = prev_response + data_main_decode
                    data_recv_from_mainplit = data_main_decode.strip().split("\n")
                    final_list = []
                    for i in data_recv_from_mainplit:
                        if not(i=="-1" or i == ""):
                            final_list.append(i)
                    if(len(final_list))>=2:
                        line_no = int(final_list[0])
                        line_text = final_list[1]
                        with line_lock:
                            if line_no not in lines:
                                lines[line_no] = line_text
                                # print(len(lines))
                                datatobeadded = final_list[0]+"\n"+final_list[1]+"\n"
                                for i in client_ip:
                                    dict_queues[i].put(datatobeadded)
                                    # print(dict_queues[i].get())
                    prev_response = ""
                else:
                    prev_response = prev_response + data_main_decode
        except:
            prev_response = ""
            recv_from_main.connect(recv_from_mainerver)
            print("connection broken with main server")
            continue


def handle_rec_client(client_socket, client_address):
    client_socket.settimeout(5)
    print(f"Accepted connection from {client_address} (receiving)")
    prev_response = ""
    while True:
        with line_lock:
            if len(lines)>=1000:
                print(f"handle_rec_client = {client_address[0]}")
                return
        data = None
        try:
            data = client_socket.recv(4096).decode('utf-8')
        except:
            print("Timeout: No data received for 5 seconds.")
            continue

        if not data:
            continue
        if not data.endswith('\n'):
            prev_response = prev_response + data
        else:
            data = prev_response + data
            data_split = data.strip().split("\n")
            final_list = []
            for i in data_split:
                if not(i=="-1" or i==""):
                    final_list.append(i)
            if(len(final_list)>=2):
                line_no = int(final_list[0])
                line_text = final_list[1]
                with line_lock:
                    if line_no not in lines:
                        lines[line_no] = line_text
                        for i in client_ip:
                            if i!= client_address[0]:
                                dict_queues[i].put(data)
            final_list = []
            prev_response = ""
            response = "received"
            client_socket.send(response.encode('utf-8'))


def handle_send_client(client_socket, client_address):
    response = None
    while True:
        with line_lock:
            if len(lines)>=1000 and dict_queues[client_address[0]].qsize()==0:
                print(f"sending to {client_address[0]} finished")
                return
        queuesize = dict_queues[client_address[0]].qsize()
        if queuesize!=0:
            # print(queuesize)
            message = dict_queues[client_address[0]].get()
            client_socket.send(message.encode('utf-8'))
            # print("sent", message)
            while response is None:
                response = client_socket.recv(4096).decode('utf-8')
            # print(response)
            response = None
            

rec_main_handler = threading.Thread(target=recv_mainserver)

try:
    rec_main_handler.start()
    start_time = time.time()
    while True:
        rec_client_socket, rec_client_address = rec_socket.accept()
        print(rec_client_address, "pri1")
        if rec_client_socket is not None and rec_client_address is not None:
            print(rec_client_socket, rec_client_address, "pri1")

            rec_client_handler = threading.Thread(target=handle_rec_client, args=(rec_client_socket, rec_client_address))
            rec_client_handler.start()
        
        send_client_socket, send_client_address = send_socket.accept()
        # print("hsiufhfsdhf")

        # print(send_client_address, "pri108880708")

        if send_client_socket is not None and send_client_address is not None:
            print(send_client_socket, send_client_address, "pri2")
            send_client_handler = threading.Thread(target=handle_send_client, args=(send_client_socket, send_client_address))
            send_client_handler.start()
finally:
    rec_main_handler.join()
    rec_client_handler.join()
    send_client_handler.join()
    rec_socket.close()
    send_socket.close()
    recv_from_main.close()

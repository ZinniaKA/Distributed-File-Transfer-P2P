#CLIENT
import socket
import time
import threading
import queue
main_server = ('10.17.51.115',9801) #vayu

master_send = ('10.194.19.137',13745) #ip address and ports of master client for sending
master_recv = ('10.194.19.137',13747) #ip address and ports of master client for receiving

#sockets
msr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#timeout
msr.settimeout(5)


main_s.connect(main_server)
#dictionary for storing lines
lines = {}
#locks spplied whenever we want to check the number of lines
lock_lines = threading.Lock()
counter = 0
#queue used by slave client for sending to master
normal_queue = queue.Queue()
def recv_server():
    #reading lines from vayu
    while True:
        prev_response = ""
        print("server connected to vayu")
        try:
            #print("1")
            while True:
                with lock_lines:
                    #print("2")
                    if len(lines) >= 1000:
                        
                        end = time.time()
                        print(end-begin)
                        return final_checker()
                message = "SENDLINE\n"
                #print("3")
                main_s.sendall(message.encode('utf-8'))
                #print("4")
                data_main = main_s.recv(4096)
                #print("5")
                data_main_decode = data_main.decode('utf-8')
                #print("6")
                if data_main_decode=='-1\n\n'  or data_main_decode == '-1\n':
                    continue
                elif data_main_decode.endswith('\n'):
                    #print("7")
                    data_main_decode = prev_response + data_main_decode
                    data_main_split = data_main_decode.strip().split("\n")
                    final_list = []
                    for i in data_main_split:
                        if not(i=="-1" or i == ""):
                            final_list.append(i)
                    if(len(final_list))>=2:
                        #print("8")
                        line_no = int(final_list[0])
                        line_text = final_list[1]
                        #print("9")
                        with lock_lines:
                            #print("10")
                            if line_no not in lines:
                                lines[line_no] = line_text
                                #print(len(lines))
                                normal_queue.put(data_main_decode)
                    prev_response = ""
                else:
                    prev_response = prev_response + data_main_decode
        except:
            prev_response = ""
            main_s.connect(main_server)
            print("connection broken with main server")
            continue

def send_masterclient():
    #sending lines to master client
    while True:
        try:
            #print("trying")
            while True:
                mss.connect(master_send)
                #print("succeeded")
                while True:
                    with lock_lines:
                        if normal_queue.qsize()== 0 and len(lines) >= 1000:
                            return 
                    response = None
                    messagel = normal_queue.get()
                    #print(normal_queue.get())
                    #print("sending")
                    if messagel is not None:
                        mss.send(messagel.encode('utf-8'))
                        #print("sending stuff to master")

                        while response is None:
                            response = mss.recv(4096).decode('utf-8')
                            #print(f"Received from server (sending): {response}")
                        response = None

        except:
            mss.connect(master_send)
            print("@@@@@@@@@disconnected from master while sending@@@@@@@")
            continue


def rec_master():
    msr.connect(master_recv)
    #receiving from master
    while True:
        try:
            response = None
            prev_response = ""
            while True:
                with lock_lines:
                    if len(lines)>= 1000:
                        print("finish from master")
                        return 
                data = None
                try:
                    #print("gggggg")
                    data1 = msr.recv(4096)
                    
                    #print("0000000000$$$$$$$$")
                    data = data1.decode('utf-8')
                    
                except:
                    print("Timeout : no data received")
                    continue
                
                if not data:
                    continue
                
                if data=="-1\n\n"  or data == "-1\n":
                    continue
                elif data.endswith("\n"):
                    data = prev_response + data
                    data_split = data.strip().split("\n")
                    final_list = []
                    for i in data_split:
                        if not(i=="-1" or i == ""):
                            final_list.append(i)
                    
                    if(len(final_list))>=2:
                        line_no = final_list[0] 
                        line_text = final_list[1] 
                        with lock_lines:
                            if (int(line_no)) not in lines:
                                lines[int(line_no)] = line_text
                                print((len(lines))) 
                    final_list = []
                    prev_response = ""
                    response = "I received"
                    msr.send(response.encode('utf-8'))
                    print("acknowledgenment sent to master")
                else:
                    prev_response = prev_response + data
    
        except:
            print("123456")
            msr.connect(master_recv)
            continue

def final_checker(): 

    ans="SUBMIT\n"
    ans+="2021CS10109@pirate\n" + "1000\n"
    main_s.send(ans.encode('utf-8'))

    for i in range(1000):
        answ = str(i) + "\n" + lines[i] + "\n"
        # print(ans)
        main_s.send(answ.encode("utf-8"))
        
    data = main_s.recv(4096)
    print("Received data:", data.decode('utf-8')) 
    message  = "SEND INCORRECT LINES\n"
    main_s.send(message.encode('utf-8'))
    data2 = main_s.recv(4096)
    print("incorrect",data2.decode('utf-8')) 
    # Close the socket
    main_s.close()
    print("Closed socket")
    msr.close()
    mss.close()
    

receiving_master_handler = threading.Thread(target=rec_master)
rec_server_handler = threading.Thread(target=recv_server) 
send_master_client = threading.Thread(target=send_masterclient)

try:
    begin = time.time()
    rec_server_handler.start()
    send_master_client.start()
    receiving_master_handler.start()
    
    rec_server_handler.join()
    send_master_client.join()
    receiving_master_handler.join()
    

finally:
    main_s.close()
    
    print("Closed socket")
    end=time.time()
    print(end-begin)
        


    


            






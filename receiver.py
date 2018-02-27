from socket import *
import time
import random

rcvIP = "localhost"
rcvPort = 12000

packet_loss_prob = eval(input("packet loss probability: "))

rcvSocket = socket(AF_INET, SOCK_DGRAM)
rcvSocket.bind((rcvIP, rcvPort))
# retrieve receiving buffer size of socket
rcvbuf = rcvSocket.getsockopt(SOL_SOCKET, SO_RCVBUF)
print("\nsocket recv buffer size :", rcvbuf)

if rcvbuf < 10000000:
    # adjust receiving buffer size to 7.4 MB
    rcvSocket.setsockopt(SOL_SOCKET, SO_RCVBUF, 7400000)
    rcvbuf = rcvSocket.getsockopt(SOL_SOCKET, SO_RCVBUF)
    print("socket recv buffer size updated :", rcvbuf)

print("The server is ready to receive", end="\n\n")

expectedSeq = -1    # keeps the seq number value the receiver is expecting to receive
flag = 0

while True:
    message, clientAddress = rcvSocket.recvfrom(2048)
    message = message.decode()

    if flag == 0:
        flag = 1
        baseTime = time.time()

    print("\t{0:0.4f} pkt: {1:s} Receiver < Sender".format(time.time() - baseTime, message))

    if random.random() < packet_loss_prob:
        print("\t{0:0.4f} ptk: {1:s} | Dropped".format(time.time() - baseTime, message))
        continue

    # packet was received in order
    if int(message) == expectedSeq + 1:
        expectedSeq = expectedSeq + 1

    print("\t{0:0.4f} ACK: {1:d} Receiver > Sender".format(time.time() - baseTime, expectedSeq))
    rcvSocket.sendto(str(expectedSeq).encode(), clientAddress)


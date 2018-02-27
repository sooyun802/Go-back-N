from socket import *
import time
import threading
from threading import Lock


# class Pkt holds a packet's info
class Pkt:
    def __init__(self, seqNum, time):
        self._seqNum = seqNum
        self._time = time

    def getSeqNum(self):
        return self._seqNum

    def getTime(self):
        return self._time

    def setTime(self, time):
        self._time = time


windowSize = eval(input("Window size: "))
timeOut = eval(input("Timeout(sec): "))
packetNum = eval(input("How many packets to send? "))
if input("Do you want to start?(y/n): ") not in ("y", "Y"):
    exit(0)
print("")

windowLock = Lock()

window = [] # packets that have been sent are stored in the window
pktSndNum = 0
ACK = -1    # ACK number sender is expecting to receive
init_time = time.time()


def listener():
    global sndSocket
    global ACK
    global init_time
    global window
    global packetNum

    while True:
        ack, rcvAddress = sndSocket.recvfrom(2048)
        ack = int(ack.decode())
        print("\t{0:0.4f} ACK: {1:d} Sender < Receiver".format(time.time() - init_time, ack))

        with windowLock:
            if ack <= ACK:
                continue

            ACK = ack
            for tmp in window:
                if tmp.getSeqNum() <= ACK:
                    window.remove(tmp)

            if ACK == packetNum - 1:
                break


rcvIP = "localhost"
rcvPort = 12000

sndSocket = socket(AF_INET, SOCK_DGRAM)
sndSocket.bind(("localhost", 0))

t = threading.Thread(target=listener, args=())
t.start()

while True:
    with windowLock:
        # stop when all packets have been received by the receiver
        if ACK == packetNum - 1:
            break

    # timeout
    with windowLock:
        if len(window) > 0 and time.time() - window[0].getTime() >= timeOut:
            print("\n\t{0:0.4f} pkt: {1:d} | Timeout since\t{2:0.4f}".format(time.time() - init_time, \
                                            window[0].getSeqNum(), window[0].getTime() - init_time), end="\n\n")
            for tmp in window:
                sndSocket.sendto(str(tmp.getSeqNum()).encode(), (rcvIP, rcvPort))
                tmp.setTime(time.time())
                print("\t{0:0.4f} pkt: {1:d} Sender > Receiver <retransmitted>".format(time.time() - init_time, tmp.getSeqNum()))
            continue

        # if window is full
        if len(window) == windowSize:
            continue

    # initialize packet transmission starting time
    if pktSndNum == 0:
        init_time = time.time()

    # window is not full
    if pktSndNum < packetNum:
        pkt = Pkt(pktSndNum, time.time())

        with windowLock:
            window.append(pkt)

        sndSocket.sendto(str(pkt.getSeqNum()).encode(), (rcvIP, rcvPort))
        print("\t{0:0.4f} pkt: {1:d} Sender > Receiver".format(time.time() - init_time, pkt.getSeqNum()))
        pktSndNum = pktSndNum + 1

sndSocket.close()
finalTime = time.time()
print("\n\t{0:0.4f} | {1:d} packet transmission completed. Throughput: {2:0.2f} pkts/sec".format(finalTime - init_time, \
                                                                packetNum, float(packetNum) / (finalTime - init_time)))

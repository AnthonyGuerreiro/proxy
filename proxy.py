#!/usr/bin/python

# Copied from http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/
# python proxy.py -h : displays usage

# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
import socket
import select
import time
import sys

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
forward_to = ('localhost', 9998)

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}
    in_host = ""
    in_port = 0
    out_host = ""
    out_port = 0

    def __init__(self, in_host, in_port, out_host, out_port):
        self.in_host = in_host
        self.in_port = in_port
        self.out_host = out_host
        self.out_port = out_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.in_host, self.in_port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        print "Initializing proxy from %s:%d to %s:%d" % (self.in_host, self.in_port, self.out_host, self.out_port)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(self.out_host, self.out_port)
        clientsock, clientaddr = self.server.accept()
        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        print self.s.getpeername(), "has disconnected"
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        print data
        self.channel[self.s].send(data)

def display_usage():
    print "python %s -h: prints this help" % sys.argv[0]
    print "python %s [in_port] [out_host] [out_port]: starts proxy in local port [in_port] forwarding to [out_host]:[out_port]" % sys.argv[0]

if __name__ == '__main__':
        if (len(sys.argv) != 1 and sys.argv[1] == '-h'):
            display_usage();
            sys.exit(1)

        in_port = sys.argv[1] if len(sys.argv) > 1 else "8080"
        out_host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        out_port = sys.argv[3] if len(sys.argv) > 3 else "80"

        server = TheServer('', int(in_port), out_host, int(out_port))
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
sys.exit(1)

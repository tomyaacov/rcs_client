import socket
import time


my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (('localhost', 6000))
out_string = "(init MyTeam (version 15))"
my_socket.sendto(out_string.encode('utf-8'), addr)

for i in range(40):
    time.sleep(0.02)
    in_string, addr = my_socket.recvfrom(10024)
    print("in string:", in_string.decode())

while True:
    #out_string = input("Enter string to send:")
    #print(out_string)
    out_string = "(move 0 0)"
    out_string += "\0"
    my_socket.sendto(out_string.encode('utf-8'), addr)
    for i in range(10):
        time.sleep(0.02)
        in_string, addr = my_socket.recvfrom(10024)
        print("in string:", in_string.decode())

    out_string = "(dash 65)"
    out_string += "\0"
    my_socket.sendto(out_string.encode('utf-8'), addr)

    for i in range(10):
        time.sleep(0.02)
        in_string, addr = my_socket.recvfrom(10024)
        print("in string:", in_string.decode())



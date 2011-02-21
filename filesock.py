import socket, os, math, select, threading,time

t_split_size = 1024
t_path = 'a.log'

t_dir = os.path.dirname(t_path)
t_size = os.path.getsize(t_path)

t_split_count = math.ceil(t_size / t_split_size)

print "split count:", t_split_count

sock_path = t_path + '.sock'


s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    os.remove(sock_path)
except OSError:
    pass
s.bind(sock_path)
s.listen(10)

def subSock(conn):
    print 'sub'
    data = conn.recv(1024)
    if data:
        print data
    conn.send('cctv')
    conn.close()

while True:
    conn, addr = s.accept()
    print 'accept',addr
    threading.Thread(target=subSock, args=(conn,)).start()

import socket, os, math, select, threading, time


class subServer(threading.Thread):
    package_size = 1024
    group_count = 3
    group_list = []
    group_pos = []
    group_last = []
    group_lock = []
    need_stop = False
    
    
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
    
    def run(self):
        thread_count = threading.activeCount() - 1 #exclude main thread
        live_group_count = self.getLiveCount()
        if live_group_count == 0:
            self.__class__.need_stop = True
            return
        
        if live_group_count > thread_count:
            self.group = self.getLastGroup() #get last end group
        else:
            self.group = self.getMinPosGroup()
            
        lock = self.__class__.group_lock[self.group]
        lock.acquire()
        pos = self.__class__.group_pos[self.group] + 1
        
        if pos >= len(self.__class__.group_list[self.group]) :
            lock.release()
            return
        
        self.__class__.group_pos[self.group] = pos
        lock.release()
        start = self.__class__.group_list[self.group][pos]
        
        #sock
        data = self.sock.recv(1024)
        if data:
            print data
        self.sock.send('cctv' + str(start))
        self.sock.close()
        
        self.__class__.group_last[self.group] = time.time()
        
    def getLiveCount(self):
        count = 0
        for i in xrange(self.__class__.group_count):
            if self.__class__.group_pos[i] + 1 < len(self.__class__.group_list):
                count = count + 1
        
        return count
        
    def getLastGroup(self):
        max_time = 0
        max_group = 0
        for i in xrange(self.__class__.group_count):
            if self.__class__.group_last[i] > max_time:
                max_time = self.__class__.group_last[i]
                max_group = i
        
        return max_group
    
    def getMinPosGroup(self):
        group = 0
        group_left = 0
        for i in xrange(self.__class__.group_count):
            left = len(self.__class__.group_list[i]) - self.__class__.group_pos[i] - 1
            if left > group_left:
                group_left = left
                group = i
        
        return group
    
if __name__ == '__main__': 
    package_size = 1024
    group_count = 3
    
    
    t_path = 'a.log'
    t_dir = os.path.dirname(t_path)
    t_size = os.path.getsize(t_path)

    package_count = math.ceil(t_size / t_split_size)
    
    

    print "split count:", t_split_count

    sock_path = t_path + '.sock'
    
    


    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove(sock_path)
    except OSError:
        pass
    s.bind(sock_path)
    s.listen(10)

    while True:
        conn, addr = s.accept()
        print 'accept',addr
        th = subServer(conn).start()
        if subServer.need_stop:
            break
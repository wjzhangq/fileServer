import socket, os, math, select, threading, time, sys
import logging


class subServer(threading.Thread):
    file_path = ''
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
        
        logging.debug("thread run info:\n\tthread_count/live group:%d/%d" % (thread_count, live_group_count))
        
        if live_group_count == 0:
            self.__class__.need_stop = True
            logging.debug("live group is zero!")
            self.sock.close()
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
            logging.debug("group full group index %d\n\tnext pos/total: %d/%d" % (self.group, pos, len(self.__class__.group_list[self.group])))
            self.sock.close()
            return
        
        self.__class__.group_pos[self.group] = pos
        lock.release()
        
        start = self.__class__.group_list[self.group][pos - 1] * self.__class__.package_size
        logging.debug("group info:\n\tgroup index:%d\n\tgroup pos/total:%d/%d" % (self.group, pos -1, len(self.__class__.group_list[self.group])))
        
        #sock
        data = self.sock.recv(1024)
        if data:
            logging.debug(data)
            
        fp = open(self.__class__.file_path, 'r')
        fp.seek(start)
        
        buff = fp.readline(1024)
        if buff:
            self.sock.sendall(buff)
        fp.close()
        self.sock.close()
        
        self.__class__.group_last[self.group] = time.time()
        
    def getLiveCount(self):
        count = 0
        for i in xrange(self.__class__.group_count):
            if self.__class__.group_pos[i] + 1 < len(self.__class__.group_list):
                count = count + 1
        
        return count
        
    def getLastGroup(self):
        max_time = -1
        max_group = 0
        for i in xrange(self.__class__.group_count):
            if (self.__class__.group_pos[i] + 1 < len(self.__class__.group_list)) and (self.__class__.group_last[i] > max_time):
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
    
    logging.basicConfig(level=logging.DEBUG)
    
    t_dir = os.path.dirname(t_path)
    t_size = os.path.getsize(t_path)

    package_count = int(math.ceil(t_size / package_size))
    group_sep = int(math.floor(package_count / group_count))
    if group_sep < 1:
        group_count = 1
        group_sep = package_count
    
    subServer.file_path = t_path
    subServer.group_count = group_count
    subServer.package_size = package_size
    
    subServer.group_list = [0 for i in xrange(group_count)]
    subServer.group_lock = [threading.RLock() for i in xrange(group_count)]
    subServer.group_pos =  subServer.group_list[:]
    subServer.group_last = subServer.group_pos[:]
    
    for i in xrange(group_count):
        start = i * group_sep
        subServer.group_list[i] = range(start,start + group_sep)

    
    if subServer.group_list[-1][-1] != (package_count -1):
        subServer.group_list[group_count -1] = range(subServer.group_list[-1][0], package_count)
    
    
    
    #debug
    logging.debug("file '%s' info:\n\tpackage size/file size: %d/%d\n\tpackage count/group count:%d/%d\n\tgroup sep: %d" % (t_path, package_size, t_size, package_count, group_count, group_sep))
    for i in xrange(group_count):
        logging.debug("group index %d\n\tstart-end:%d-%d\t%d" % (i, subServer.group_list[i][0],subServer.group_list[i][-1], len(subServer.group_list[i]),))
    

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
            pass
            #break
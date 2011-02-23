# -*- coding:utf-8 -*-

import socket, os, math, select, threading, time, sys
import logging

class fileLine:
    min_size = 1024
    def __init__(self, path, start, size):
        self.fp = open(path, 'r')
        
        mod = divmod(size, self.__class__.min_size)
        
        self.max_count = mod[0]
        self.post_count = mod[1]
        if self.max_count == 0:
            self.count = -1
        else:
            self.count = 0
        
        
        if start == 0:
            pre_buff = ''
        elif start > self.__class__.min_size:
            self.fp.seek(start - self.__class__.min_size)
            buff = self.fp.read(self.__class__.min_size)
            pos = buff.rfind("\n")
            if pos == -1:
                #error
                pre_buff = ''
            else:
                pre_buff = buff[pos+1:]
            self.fp.seek(start)
        else:
            buff = self.fp.read(start)
            pos = buff.rfind("\n")
            if pos == -1:
                pre_buff = buff
            else:
                pre_buff = buff[pos+1:]
        self.pre_buff = pre_buff
        
    def __iter__(self):
        return self
    
    def next(self):
        max_count_1 = self.max_count -1
        if self.count > max_count_1:
            self.fp.close()
            raise StopIteration
            
            
        if self.max_count == 0:
            buff = self.fp.read(self.post_count)
            pos = buff.rfind("\n")
            if pos == -1:
                #error
                pass
            else:
                buff = buff[:pos]
        else:
            if self.count == max_count_1:
                buff_count = self.__class__.min_size + self.post_count
                buff = self.fp.read(buff_count)

                if len(buff) == buff_count:
                    pos = buff.rfind("\n")
                    if pos == -1:
                        #error
                        pass
                    else:
                        buff = buff[:pos]
                else:
                    pass
            else:
                buff = self.fp.read(self.__class__.min_size)
            
        if self.count < 1:
            buff = self.pre_buff + buff
            self.pre_buff = ''
                        
        self.count = self.count + 1
        
        return buff
        

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
        debug_group_info()
        
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
        
        #开始执行时候更新时间
        self.__class__.group_last[self.group] = -1
        
        start = self.__class__.group_list[self.group][pos - 1] * self.__class__.package_size
        logging.debug("group info:\n\tgroup index:%d\n\tgroup pos/total:%d/%d" % (self.group, pos -1, len(self.__class__.group_list[self.group])))
        
        #sock
        data = self.sock.recv(1024)
        if data:
            logging.debug(data)
            
        fileObj = fileLine(self.__class__.file_path, start, self.__class__.package_size)
        for buff in fileObj:
            self.sock.sendall(buff)
        self.sock.close()
        
        #结算执行时候更新时间
        self.__class__.group_last[self.group] = time.time()
        
    def getLiveCount(self):
        count = 0
        for i in xrange(self.__class__.group_count):
            if self.__class__.group_pos[i] + 1 < len(self.__class__.group_list[i]):
                count = count + 1
        
        return count
        
    def getLastGroup(self):
        max_time = -1
        max_group = 0
        for i in xrange(self.__class__.group_count):
            if (self.__class__.group_pos[i] + 1 < len(self.__class__.group_list[i])) and (self.__class__.group_last[i] > max_time):
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
        
def debug_group_info():
    for i in xrange(subServer.group_count):
        logging.debug("\tgroup index %d\n\t\tstart-end:%d-%d\n\t\tpos/count:%d/%d" % (i, subServer.group_list[i][0],subServer.group_list[i][-1], subServer.group_pos[i] ,len(subServer.group_list[i]),))
    
    
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
    debug_group_info()
    

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
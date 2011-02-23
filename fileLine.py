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
        

if __name__ == '__main__':
    fp = fileLine('b.log', 20, 60)
    str1 = ''
    for i in fp:
        str1 += i
    print str1
    print len(str1)
    
    fp = fileLine('b.log', 80, 60)
    str1 = ''
    for i in fp:
        str1 += i
    print str1
    print len(str1)
    
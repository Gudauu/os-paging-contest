import sys
import getopt
import time

def printlog(fault, lendata,tot_time):
    print("numbers of fault:", fault, "\tnumbers of data:", lendata)
    print("ratio of fault:",format(fault/lendata,'.8f'))
    print("time elapsed(in seconds):",format(tot_time,'.8f'))

# FIFO algorithm
def fifo(data, frame_num):
    start_time = time.time()
    memory = []
    fault = 0
    oldestAddr = 0
    for page in data:
        if oldestAddr >= frame_num:
            oldestAddr -= frame_num

        if page not in memory:
            if len(memory) < frame_num:
                fault += 1
                memory.append(page)
            else:
                memory.pop(oldestAddr)
                memory.insert(oldestAddr, page)
                fault += 1
                oldestAddr += 1
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)


# LRU algorithm
def lru(data, frame_num):
    start_time = time.time()
    memory = []
    fault = 0
    last_reference = {}
    for page in data:
        for node in last_reference:
            last_reference[node] += 1
        last_reference[page] = 0
        
        if memory.count(page) == 0:     #  not exist
            if len(memory) < frame_num:
                fault += 1
                memory.append(page)
            else:
                fault += 1
                # 找最久没有被访问的node
                recently = None
                for node in last_reference:    
                    if recently == None:
                        recently = node
                        continue
                    elif last_reference[node] > last_reference[recently]:
                        recently = node
                memory[memory.index(recently)] = page
                last_reference.pop(recently)
        else:
            last_reference[page] = 0
        # print(memory, page)
        # print(last_reference)
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)


def optimal(data,frame_num):
    start_time = time.time()
    memory = []
    fault = 0
    for index, page in enumerate(data):
        if len(memory) < frame_num:
            if memory.count(page) == 0:     # not exist
                memory.append(page)
                fault += 1

        elif memory.count(page) == 0:
            fault += 1
            next_use = {}
            pick = None
            for temp in memory:
                if temp not in data[index:]:      
                    pick = temp
                    break
                else:   # use in furture
                    distance = data[index:].index(temp)
                    next_use[temp] = distance
            else:   
                for node in next_use:
                    if pick == None:
                        pick = node
                    else:
                        if next_use[node] > next_use[pick]:
                            pick = node
            
            memory[memory.index(pick)] = page
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)


# OPT algorithm
# def opt(data, frame_num):
#     fault = 0
#     memory = []
#     for page in data:
#         if page not in memory:
#             if len(memory) < frame_num:
#                 if memory.count(page) == 0:     # not exist
#                     memory.append(page)
#                     fault += 1
#             else:
#                 distance = {}
#                 for index, tmp in enumerate(memory):        #replacement
#                     if tmp not in data[index:]:

                    

# second chance algorithm
def sc(data, frame_num):
    start_time = time.time()
    memory = []
    ref_bits = {}
    fault = 0

    for page in data:
        if len(memory) < frame_num:
            if memory.count(page) == 0:     # not exist
                memory.append(page)
                ref_bits[page] = 0
                fault += 1
        else:
            if memory.count(page) == 1:
                ref_bits[page] = 1
            else:                           # replacement
                while ref_bits[memory[0]] == 1:
                    tmp = memory[0]
                    ref_bits[tmp] = 0
                    memory.pop(0)
                    memory.append(tmp)
                memory.pop(0)
                memory.append(page)
                ref_bits[page] = 0
                fault += 1
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)

def jru(data, frame_num):
    start_time = time.time()
    memory = []
    fault = 0
    mark = '-1/n'

    for page in data:
        if len(memory) < frame_num:
            if memory.count(page) == 0:     # not exist
                memory.append(page)
                fault += 1
                mark = page
        else:
            if memory.count(page) == 1:
                pass
            else:
                # delete mark
                j = 0
                for i in range(len(memory)):
                    if memory[j] == mark:
                        memory.pop(j)
                    else:
                        j += 1
                memory.append(page)
                mark = page
                fault += 1
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)

def prefetch(page,fetch_num):
    # decide on fetch number
    result = []
    dec_page = int(page,16)
    for dec_i in range(dec_page-int(fetch_num/2),dec_page+int(fetch_num/2)):
        result.append(str(hex(dec_i))[2:] + '\n')
    return result

def lru_prefetch(data, frame_num,prefetch_freq = 0):
    start_time = time.time()
    memory = []
    fault = 0
    last_reference = {}
    pref_count = 0
    if prefetch_freq == 0:
        prefetch_freq = 10
    for page in data:
        # add prefetch if this is the round
        if pref_count == 0:
            to_add = prefetch(page,prefetch_freq)
            for each in to_add:
                if each not in memory:
                    memory.append(each)
                    last_reference[each] = frame_num # give them a big number         

        for node in last_reference:
            last_reference[node] += 1
        last_reference[page] = 0
        
        if memory.count(page) == 0:     #  not exist
            if len(memory) < frame_num:
                fault += 1
                memory.append(page)
            else:
                fault += 1
                # 找最久没有被访问的node
                recently = None
                for node in last_reference:    
                    if recently == None:
                        recently = node
                        continue
                    elif last_reference[node] > last_reference[recently]:
                        recently = node
                memory[memory.index(recently)] = page
                last_reference.pop(recently)
        else:
            last_reference[page] = 0
        # print(memory, page)
        # print(last_reference)
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
        pref_count = (pref_count + 1)%prefetch_freq

    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)

    







def popular(data, frame_num):
    start_time = time.time()
    memory = []
    popular = {}
    ghost_time = {} #how many rounds has pages sit unvisited
    fault = 0

    for page in data:
        # update ghost time
        for each in memory:
            ghost_time[each] += 1
        # update popular
        if page not in popular:
            popular[page] = 0
        popular[page] += 1
        
        if page in memory:  # hit
            ghost_time[page] = 0
        else:
            fault += 1 
            ghost_thresh = 60
            if len(memory) >= frame_num:
                least_pop_value = popular[memory[0]]
                least_pop_index = 0
                for i in range(frame_num):
                    if ghost_time[memory[i]] > ghost_thresh:
                        least_pop_index = i
                        break
                    if popular[memory[i]] < least_pop_value:
                        least_pop_value = popular[memory[i]]
                        least_pop_index = i
                memory.pop(least_pop_index)

            memory.append(page)
            ghost_time[page] = 0

        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    



if __name__ == "__main__":
    # prefetch('2001f8c\n',30)
    # data = []
    # with open("mm16.txt") as file:
    #     for item in file:
    #         # print(item)
    #         data.append(item)
    # lru_prefetch(data,60,10)
    # start

    data = []
    shortargs = 'm:n:hf:p::'
    longargs = []
    opts, args = getopt.getopt( sys.argv[1:], shortargs, longargs )
    prefetch_fr = 10

    if args:
        print('-h or --help for detail')
        sys.exit(1)

    for opt,val in opts:
        if opt in ( '-h' ):
            print('No help document yet')
            sys.exit(1)
        if opt in ( '-n'):
            frame_num = int(val)
            # print(frame_num)
        if opt in ( '-m'):
            mode = val
            # print(mode)
        if opt in ( '-f'):
            filePath = val
            # print(filePath)
            with open(filePath) as file:
                for item in file:
                    # print(item)
                    data.append(item)
        if opt in ( '-p'):
            prefetch_fr = int(val)
            # print(prefetch_fr)


    if mode == "fifo":
        fifo(data, frame_num)
    elif mode == "lru":
        lru(data, frame_num)
    elif mode == "opt":
        optimal(data, frame_num)
    elif mode == "sc":
        sc(data, frame_num)
    elif mode == "jru":
        jru(data, frame_num)
    elif mode == "popu":
        popular(data, frame_num)  
    elif mode == "lru_p":
        lru_prefetch(data, frame_num,prefetch_fr)  
    
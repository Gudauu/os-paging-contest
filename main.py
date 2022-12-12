import sys
import getopt
import time
import random
from prefetch import * 

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
    for page in data:
        if page not in memory:     #  not exist
            fault += 1
            if len(memory) >= frame_num:
                memory.pop(0)  
        else: # hit
            memory.remove(page)
        memory.append(page) 
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
    

    

def random1(data, frame_num):
    start_time = time.time()
    memory = []
    fault = 0

    for page in data:
        if len(memory) < frame_num:
            if memory.count(page) == 0:     # not exist
                memory.append(page)
                fault += 1
        else:
            if memory.count(page) == 1:
                pass
            else:
                # delete random
                i = random.randint(0, frame_num-1)
                memory.pop(i)
                memory.append(page)
                fault += 1
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    rate = fault/len(data)
    return [fault, end_time-start_time]

# working set
def ws(data, frame_num, delta_F):
    memory = []
    workspace = {}
    fault = 0
    times = 0
    start_time = time.time()
    for page in data:
        if len(memory) < frame_num:
            if memory.count(page) == 0:     # not exist
                memory.append(page)
                workspace[page] = times
                fault += 1
                times += 1
        else:
            if memory.count(page) == 1:
                workspace[page] = times
                times += 1
            else:
                for m in memory:
                    delta = times - workspace[m]
                    if delta >= delta_F:
                        memory.remove(m)
                        break
                else:
                    memory.pop(1)
                memory.append(page)
                workspace[page] = times
                fault += 1
                times += 1
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    rate = fault/len(data)
    return rate

if __name__ == "__main__":
    # data = []
    # with open("sort1.txt") as file:
    #     for item in file:
    #         # print(item)
    #         data.append(item)
    # fifo_prefetch(data,30,0)
    # -m mode
    # -n frame number
    data = []
    shortargs = 'd:m:n:hf:p::i::'
    longargs = []
    opts, args = getopt.getopt( sys.argv[1:], shortargs, longargs )
    prefetch_num = 0


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
        if opt in ('-d'):
            delta = int(val)
        # the prefetch frequency and number of pages to fetch are the same, assigned here
        if opt in ( '-p'):
            prefetch_num = str(val)

    if mode == "fifo":
        if prefetch_num == 0:
            fifo(data, frame_num)
        else:
            fifo_prefetch(data, frame_num,prefetch_num)
    elif mode == "lru":
        if prefetch_num == 0:
            lru(data, frame_num)
        else:
            lru_prefetch(data,frame_num,prefetch_num)
    elif mode == "opt":
        optimal(data, frame_num)
    elif mode == "sc":
        sc(data, frame_num)
    elif mode == "jru":
        if prefetch_num == 0:
            jru(data, frame_num)
        else:
            jru_prefetch(data, frame_num,prefetch_num)
    elif mode == "popu":
        if prefetch_num == 0:
            popular(data, frame_num)  
        else:
            popular_prefetch(data,frame_num,prefetch_num)
    elif mode == "random":
        if prefetch_num == 0:
            random1(data, frame_num)  
        else:
            random1_prefetch(data,frame_num,prefetch_num)
        # tmp1 = 0
        # tmp2 = 0
        # times = 100
        # for i in range(1, times):
        #     tmp1 += random1(data, frame_num)[0]
        #     tmp2 += random1(data, frame_num)[1]
        # printlog(tmp1, len(data), tmp2/times)
    elif mode == "ws":
        if prefetch_num == 0:
            ws(data, frame_num, delta)
        else:
            ws_prefetch(data, frame_num, delta,prefetch_num)

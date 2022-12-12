import sys
import getopt
import time
import random

def printlog(fault, lendata,tot_time):
    print("numbers of fault:", fault, "\tnumbers of data:", lendata)
    print("ratio of fault:",format(fault/lendata,'.8f'))
    print("time elapsed(in seconds):",format(tot_time,'.8f'))

# return a list of in total fetch_num pages before and after "page"
def prefetch(page,fetch_num):
    # decide on fetch number
    result = []
    dec_page = int(page,16)
    for dec_i in range(dec_page-int(fetch_num/2),dec_page+int(fetch_num/2)):
        result.append(str(hex(dec_i))[2:] + '\n')
    return result

# FIFO algorithm
def fifo_prefetch(data, frame_num,prefetch_num):
    start_time = time.time()
    memory = []
    fault = 0
    last_page = '0'
    prefetch_when_full = (prefetch_num[0] == '0')
    if prefetch_when_full and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

    for page in data:
        if page not in memory:
            fault += 1
            if len(memory) >= frame_num:
                memory.pop(0)
            memory.append(page)

        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) >= frame_num and prefetch_when_full:
                        memory.pop(0)
                        memory.append(np)
                    elif len(memory) < frame_num:
                        memory.append(np)

        last_page = page
                    
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)


# LRU algorithm with prefetch
def lru_prefetch(data, frame_num,prefetch_num):
    start_time = time.time()
    memory = []
    fault = 0
    # prefetch parameters
    last_page = '0'
    prefetch_when_full = (prefetch_num[0] == '0')
    if prefetch_when_full and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

    # start access memory
    for page in data:
        if page not in memory:     #  not exist
            fault += 1
            if len(memory) >= frame_num:
                memory.pop(0)  
        else: # hit
            memory.remove(page)
        memory.append(page) 
        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) >= frame_num and prefetch_when_full:
                        memory.pop(0)
                        memory.append(np)
                    elif len(memory) < frame_num:
                        memory.append(np)
        last_page = page

        # print(memory, page)
        # print(last_reference)
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)



def optimal_prefetch(data,frame_num):
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

def jru_prefetch(data, frame_num,prefetch_num):
    start_time = time.time()
    memory = []
    fault = 0
    mark = '-1/n'
    # prefetch: only fill when there's empty slot
    # prefetch parameters
    last_page = '0'
    if (prefetch_num[0] == '1') and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

    for page in data:
        if len(memory) < frame_num:
            if page not in memory:     # not exist
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
        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) < frame_num:
                        memory.append(np)
                        mark = page

        last_page = page
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)


def popular_prefetch(data, frame_num,prefetch_num):
    start_time = time.time()
    memory = []
    popular = {}
    ghost_time = {} #how many rounds has pages sit unvisited
    fault = 0
    # prefetch parameters. Only add when not full
    last_page = '0'
    if (prefetch_num[0] == '0') and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

    for page in data:
        # update ghost time
        for each in memory:
            if each not in ghost_time: # prefetched pages
                ghost_time[each] = frame_num
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

        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) < frame_num:
                        memory.append(np)
                        # update popular
                        if np not in popular:
                            popular[np] = 0
        last_page = page

        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    

    

def random1_prefetch(data, frame_num,prefetch_num):
    start_time = time.time()
    memory = []
    fault = 0
    # prefetch parameters
    last_page = '0'
    prefetch_when_full = (prefetch_num[0] == '0')
    if prefetch_when_full and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

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
        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) >= frame_num and prefetch_when_full:
                        i = random.randint(0, frame_num-1)
                        memory.pop(i)
                        memory.append(np)
                    elif len(memory) < frame_num:
                        memory.append(np)
        last_page = page
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    rate = fault/len(data)
    return [fault, end_time-start_time]

# working set
def ws_prefetch(data, frame_num, delta_F,prefetch_num):
    memory = []
    workspace = {}
    fault = 0
    times = 0
    # prefetch parameters. Only add when not full
    last_page = '0'
    if (prefetch_num[0] == '0') and not (len(prefetch_num)==1):
        prefetch_num = int(prefetch_num[1:])
    else:
        prefetch_num = int(prefetch_num)

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
        # prefetch if found two adjacent pages
        if abs(int(page,16) - int(last_page,16)) < (prefetch_num-1):
            to_add = prefetch(page,prefetch_num)
            for np in to_add:
                if np not in memory:
                    if len(memory) < frame_num :
                        memory.append(np)
                        workspace[np] = times
        last_page = page
        # print(page, '\t',memory, "\nnumbers of fault:", fault)
    end_time = time.time()
    printlog(fault, len(data),end_time-start_time)
    rate = fault/len(data)
    return rate


    


import shelve
import sys
import binascii
import threading

db = shelve.open('danmuhash')

countL = [0]
def create_hash(index,lock):
	for x in range(index[0],index[1]):
		temp = "%.8x" % (binascii.crc32('%s' % x) & 0xffffffff)
		countL[0] = countL[0] + 1
		sys.stdout.write("\r"+"%.4g%%, %s / 50000000  " % (countL[0]/500000.0,countL[0]))
		sys.stdout.flush()
		lock.acquire()
		db[temp] = x
		lock.release()

def create_index_table(length,maxNumOfThread=20,start=0):
	number_of_thread = abs(length-start)/5+1
	if number_of_thread > maxNumOfThread:
		number_of_thread = maxNumOfThread
	dx = (length-start)/number_of_thread
	end = start+dx
	index = []
	for x in range(number_of_thread):
		if x == number_of_thread-1:
			end = length
		index.append((start,end))
		start = start + dx
		end = end + dx
	return index

index = create_index_table(50000000,50)
threads = []
lock = threading.Semaphore()
for i in range(len(index)):
	t1 = threading.Thread(target=create_hash, args = (index[i],lock))
	t1.daemon = True
	t1.start()
	threads.append(t1)

for x in threads:
	x.join()

db.close()
print("\nDone.")
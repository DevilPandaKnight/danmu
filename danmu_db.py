#!/usr/bin/python
# -*- coding: utf-8 -*-
#作者：Jin
#改自: http://www.gn00.com/t-462442-1-1.html
# 哔哩哔哩历史弹幕 (XML) 下载器
# 使用：danmu.py av*****
from optparse import OptionParser
import sys
import binascii
import threading
import StringIO
import datetime
import gzip
import json
import os
import re
import urllib2
import zlib
import shelve

def get_danmu(json_data,cid,folder,index):
	for i in range(index[0],index[1]):
		comment_timestamp = json_data[i]['timestamp']
		comment_date = datetime.datetime.fromtimestamp(int(comment_timestamp)).strftime('%Y%m%d')
		comment_then_url = 'http://comment.bilibili.tv/dmroll,%s,%s' % (comment_timestamp, cid)
		comment_then_request = urllib2.Request(comment_then_url)
		comment_then_zip = urllib2.urlopen(comment_then_request).read()
		comment_then_xml = zlib.decompressobj(-zlib.MAX_WBITS).decompress(comment_then_zip)
		comment_file = open('%s/%s.xml' % (folder, comment_date), 'wb')
		comment_file.write(comment_then_xml)
		comment_file.close()
	
def get_danmu_to_set(json_data,cid,danmu_set,index):
	for i in range(index[0],index[1]):
		comment_timestamp = json_data[i]['timestamp']
		comment_date = datetime.datetime.fromtimestamp(int(comment_timestamp)).strftime('%Y%m%d')
		comment_then_url = 'http://comment.bilibili.tv/dmroll,%s,%s' % (comment_timestamp, cid)
		comment_then_request = urllib2.Request(comment_then_url)
		comment_then_zip = urllib2.urlopen(comment_then_request).read()
		comment_then_xml = zlib.decompressobj(-zlib.MAX_WBITS).decompress(comment_then_zip)
		danmu_set[0] = danmu_set[0].union(comment_then_xml.split('\n'))

countL = [0]
def add_user_name(danmu,index,hash_table,max_num):
	max_num = float(max_num)
	for i in range(index[0],index[1]):
		countL[0] = countL[0] + 1
		sys.stdout.write("\r"+"%.4g%%, %s / %d     " % (countL[0]/max_num*100,countL[0],max_num))
		sys.stdout.flush()
		d = danmu[i]
		sp = d.split(',')
		if len(sp) >= 7:
			if sp[6] in hash_table:
				try:				
					video_page_url = 'http://space.bilibili.com/%s' % hash_table[sp[6]]
					video_page_request = urllib2.Request(video_page_url)
					video_page_gz = urllib2.urlopen(video_page_request).read()
					start = video_page_gz.find("<title>")+7
					end = video_page_gz.find("的个人空间")
					new = video_page_gz[start:end]
					danmu[i] = d+"\n用户名: "+new+'\n-----------------------------------------------------\n'
					#print(d+"\n用户名: "+new+'\n-----------------------------------------------------\n')
				except:
					print("cannot open: "+video_page_url)
			else:
				danmu[i] = "%s\n%s%s" % ("has no hash "+ sp[6], d,'\n-----------------------------------------------------\n') 
				#print("%s\n%s%s" % ("has no hash "+ sp[6], d,'\n-----------------------------------------------------\n') )


def create_index_table(length,maxNumOfThread=20):
	number_of_thread = length/5+1
	if number_of_thread > maxNumOfThread:
		number_of_thread = maxNumOfThread
	dx = length/number_of_thread
	start = 0
	end = dx
	index = []
	for x in range(number_of_thread):
		if x == number_of_thread-1:
			end = length
		index.append((start,end))
		start = start + dx
		end = end + dx
	return index
		

def parse_xml(xml_file):
	print("正在初始化hash表...")
	hash_table = shelve.open('danmuhash')
		
	try:
		danmu_list = [x.strip() for x in open(xml_file)]
		index = create_index_table(len(danmu_list))
	except IOError:
		print("cannot open the file %s" % xml_file)
		hash_table.close()
		exit()

	user_Thread = []
	for i in range(len(index)):
		t1 = threading.Thread(target=add_user_name, args = (danmu_list,index[i],hash_table,len(danmu_list)))
		t1.daemon = True
		t1.start()
		user_Thread.append(t1)

	for x in user_Thread:
		x.join()
	print("")
	for x in danmu_list:
		print(x)
	hash_table.close()

def main():
	#define massages
	version_msg = "%prog 1.0"
	usage_msg = """%prog danmu [-acnsf]
The following options shall be supported:
-a, --av
	输入av号码，如：av3934631，或者 av3934631/index_1.html
-c, --cid
	输入cid号码，如：6645564
-n
	在所有弹幕后面加用户名 (用时较长).
-s
	把弹幕以时间分到不同的文件夹里.
-f
	接受一个弹幕xml文件，然后打印出用户名和弹幕
	"""
	#define options
	parser = OptionParser(version=version_msg,usage=usage_msg)
	parser.add_option("-n", action="store_true", default=False,help="在所有弹幕后面加用户名 (用时较长).")
	parser.add_option("-s", action="store_true", default=False,help="把弹幕以时间分到不同的文件夹里.")
	parser.add_option("-a", "--av" ,dest="av_number", default='',help="输入av号码，如：av3934631，或者 av3934631/index_1.html")
	parser.add_option("-c", "--cid", dest="cid_number", default='',help="输入cid号码，如：6645564")
	parser.add_option("-f", "--file", dest="xml_file", default='',help="接受一个弹幕xml文件，然后打印出用户名和弹幕")
	options, args = parser.parse_args(sys.argv[1:])
	if len(options.xml_file) != 0:
		parse_xml(options.xml_file)
		exit()
	
	av_number = ''
	if len(args) == 1 and args[0].startswith('av'):
		av_number = args[0]
	elif len(args) == 0 and options.av_number.startswith('av'):
		av_number = options.av_number
	if len(av_number) == 0 and len(options.cid_number) == 0:
		parser.error("wrong number of operands")
	

	cid_number = ''
	if len(av_number) != 0:
		# 处理 bilibili 视频页面
		video_page_url = 'http://www.bilibili.tv/video/%s' % av_number
		video_page_request = urllib2.Request(video_page_url)
		video_page_gz = urllib2.urlopen(video_page_request).read()
		# gzip 解压
		# 方法来自 [url]http://stackoverflow.com/a/3947241[/url]
		video_page_buffer = StringIO.StringIO(video_page_gz)
		video_page_html = gzip.GzipFile(fileobj = video_page_buffer).read()
		 
		# 获取视频 cid
		try:
			cid_number = re.findall(r'cid=(\d+)', video_page_html)[0]
		except IndexError:
			if len(options.cid_number) == 0:
				print('找不到cid号码，请输入cid号码')
				exit()
	
	if len(cid_number) == 0:
		cid_number = options.cid_number
	
	# 获取视频所有历史弹幕
	comments_page_url = 'http://comment.bilibili.tv/rolldate,%s' % cid_number
	comments_page_request = urllib2.Request(comments_page_url)
	comments_page_zip = urllib2.urlopen(comments_page_request).read()
	# deflate 解压
	# 方法来自 [url]http://stackoverflow.com/a/9583564[/url]
	comments_page_json = zlib.decompressobj(-zlib.MAX_WBITS).decompress(comments_page_zip)
	
	# 解析历史弹幕信息
	total_danmu = [set()]
	comments_python_object = json.loads(comments_page_json)
	print("正在下载弹幕...")
	index = create_index_table(len(comments_python_object),50)
	danmu_Thread = []
	if options.s == True:
		if len(av_number) == 0:
			av_number = 'cid'+cid_number
		xml_folder = r'./%s' % av_number
		if os.path.exists(xml_folder):
			pass
		else:
			os.makedirs(xml_folder)
		for i in range(len(index)):
			t1 = threading.Thread(target=get_danmu, args = (comments_python_object,cid_number,xml_folder,index[i]))
			t1.daemon = True
			t1.start()
			danmu_Thread.append(t1)
		for x in danmu_Thread:
			x.join()
		exit()
	else:
		for i in range(len(index)):
			t1 = threading.Thread(target=get_danmu_to_set, args = (comments_python_object,cid_number,total_danmu,index[i]))
			t1.daemon = True
			t1.start()
			danmu_Thread.append(t1)

		
	for x in danmu_Thread:
		x.join()
		
	
	if options.n:
		hash_table = shelve.open('danmuhash')
		danmu_list = list(total_danmu[0])
		index = create_index_table(len(danmu_list),10)
		user_Thread = []
		print("正在下载用户名单:")
		for i in range(len(index)):
			t1 = threading.Thread(target=add_user_name, args = (danmu_list,index[i],hash_table,len(danmu_list)))
			t1.daemon = True
			t1.start()
			user_Thread.append(t1)

		for x in user_Thread:
			x.join()
		print("")
		for x in danmu_list:
			print(x)
		hash_table.close()
		exit()
		
	for x in total_danmu[0]:
		print(x)		
	
if __name__ == "__main__":
	main()
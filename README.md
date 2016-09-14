# danmu
弹幕下载代码
1. 先运行来建立hash表:
python create_hash.py
2. 可以直接下载弹幕
python danmu_db.py av＊＊＊＊
3. 可以在弹幕后面加用户名（需要第一步完成才行）：
python danmu_db.py av＊＊＊＊ －n

注意某些合集视频输入av号之后会提示找不到cid号码，那么就需要在chrome中打开那个视频，然后右键打开网页源代码，搜索cid号码
然后输入cid号码
4. 输入cid号码：
python danmu_db.py －c 12345 －n

有些合集的url地址会是av＊＊＊＊／index_1.html，那么就要把后面的index部分也加进来
5.
python danmu_db.py av＊＊＊＊／index_1.html －n

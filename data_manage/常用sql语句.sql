USE fund_stream;
SELECT COUNT(*) FROM total ;
SELECT COUNT(*) FROM total WHERE LENGTH(m3u8_url) > 0;

SELECT COUNT(*) FROM total;
SELECT * FROM total WHERE CODE = 4336647;

UPDATE total SET m3u8_url = 'https://1500000598.vod2.myqcloud.com/438174e6vodtranscq1500000598/c6513b085576678020788331322/v.f230.m3u8' WHERE CODE = 4340048;

SELECT CODE,m3u8_url FROM total WHERE ((downloaded=''OR downloaded IS NULL) AND (occupied IS NULL OR occupied='') AND (LENGTH(m3u8_url)>0))

# 已经下载的MP3的数量
SELECT COUNT(*) FROM total WHERE (downloaded=1);

# 已经有下载链接但没下载的数量
SELECT COUNT(*) FROM total WHERE (LENGTH(m3u8_url)<>0 AND downloaded IS NULL);

#已经有下载链接的
SELECT COUNT(*) FROM total WHERE (LENGTH(m3u8_url)<>0 AND downloaded);


# 检查是否有已经下载但是没有下载连接的
SELECT COUNT(*) FROM total WHERE (downloaded<>1 AND LENGTH(m3u8_url) <> 0);

UPDATE total SET downloaded =1  WHERE CODE = 999;

# 已经转录的MP3的数量
SELECT COUNT(*) FROM total WHERE (stt=1);

# 选择一个没被下载过且不是正在被占用的
SELECT CODE FROM total WHERE (downloaded IS NULL AND occupied IS NULL);

# 重置一天前的occupy

SELECT COUNT(*) FROM total WHERE (downloaded =1 AND occupied IS NULL AND DATE>'2023-09-01') ORDER BY `date`;

UPDATE total SET occupied =1,occupied_time="2024-02-22 13:39:19"  WHERE CODE = 3850111;

SELECT COUNT(CODE) FROM total WHERE LENGTH(m3u8_url)=0;

SELECT CODE,DATE FROM total WHERE LENGTH(m3u8_url)=0 ORDER BY `date` DESC;

SELECT * FROM total WHERE (LENGTH(m3u8_url)=0 OR ISNULL(m3u8_url))ORDER BY `date` DESC;

SELECT COUNT(*) FROM total WHERE (LENGTH(m3u8_url)=0 OR ISNULL(m3u8_url));

SELECT COUNT(*) FROM total WHERE (LENGTH(m3u8_url)<>0 );

SELECT COUNT(*) FROM total WHERE downloaded =1;

#新的url总数目 25103
SELECT COUNT(* )FROM total WHERE LENGTH(m3u8_url_new)>0;

# 之前下载错的url   14775 
SELECT COUNT(* )FROM total WHERE (LENGTH(m3u8_url)>0 AND LENGTH(m3u8_url_new)>0 AND m3u8_url<>m3u8_url_new);
 

# 判断新的url有没有重复的
SELECT m3u8_url_new, COUNT(m3u8_url_new) AS COUNT
FROM total
GROUP BY m3u8_url_new
HAVING COUNT > 1
ORDER BY COUNT DESC;

UPDATE total SET downloaded=NULL WHERE m3u8_url<>m3u8_url_new;

# 本来正确下载的数目
SELECT COUNT(*) FROM total WHERE LENGTH(m3u8_url)>0 AND m3u8_url=m3u8_url_new;

# 查找不重复的code的条数
SELECT COUNT(*) FROM (SELECT DISTINCT CODE FROM opinions) AS distinct_codes;

# 知道opinions里的直播的日期，并统计每个日期有多少场直播
# 从opinions里的code字段，去total表里找到date，并统计每个日期有多少场直播
SELECT DATE,COUNT(*) FROM total WHERE CODE IN (SELECT distinct CODE FROM opinions) GROUP BY DATE;



# 先从opinions里的code字段，去total表里找到date，找到date为null的行
SELECT count(*) FROM total WHERE CODE IN (SELECT distinct CODE FROM opinions) AND DATE IS NULL;

# 查看total表里的每个date有多少条
SELECT DATE,COUNT(*) FROM total GROUP BY DATE;

select count(code) from total where date>'2023/11/22';
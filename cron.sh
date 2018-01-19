yesterday=`date '+%Y%m%d' -d 'yesterday'`

echo $yesterday
curl http://lifelongedu.kmoocs.kr/excel_download/$yesterday >> /home/project/management/cronlog

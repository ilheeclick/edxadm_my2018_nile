yesterday=`date '+%Y%m%d' -d 'yesterday'`

echo $yesterday
curl http://lifelongedu.kmoocs.kr/excel_download3/$yesterday >> /home/project/management/cronlog

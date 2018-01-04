import csv
 
f = open('win.csv', 'r')
rdr = csv.reader(f, dialect=csv.excel_tab)
for line in rdr:
    print(line)
f.close()    

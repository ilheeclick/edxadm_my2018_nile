import openpyxl
 
wb = openpyxl.load_workbook('496f60c5306e4204847faf43a30c8652.xlsx')
 
ws = wb.active
 
for r in ws.rows:
    print r
    #row_index = r[0].row
    #kor = r[1].value
    #eng = r[2].value
    #math = r[3].value
    #sum = kor + eng + math
    #ws.cell(row=row_index, column=5).value = sum
    #print(kor, eng, math, sum)
 
#wb.save("score2.xlsx")
wb.close()

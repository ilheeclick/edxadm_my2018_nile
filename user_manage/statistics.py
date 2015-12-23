from django.db import connection
import xlsxwriter
import views
import query

def statistics_excel():

    views.main_query()

    workbook = xlsxwriter.Workbook('/work1/statistics_excel/basic.xlsx')
    worksheet1 = workbook.worksheets('서비스 일일 통계')

    worksheet1.write('A1', 'Hello')

    workbook.close(views.time)
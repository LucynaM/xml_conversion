
from datetime import datetime
from .process_xml_data import fast_iter, get_headers, change_data

# filling excel sheet with xml parsed data
def fill_sheet(headers, sheet, results, obj, bold, date, money, numbers, strings):

    col = 0
    row = 1
    for header in headers:
        sheet.write(0, col, header, bold)
        if 'K_' in header:
            sheet.set_column(col, col, 10)
        else:
            sheet.set_column(col, col, len(header))
        col += 1

    for result in results:
        col = 0
        for header in headers:

            if header in result.keys() and result[header] != None:
                if header in obj.date_fields:
                    sheet.write(row, col, datetime.strptime(result[header], '%Y-%m-%d'), date)
                elif header in obj.money_fields:
                    sheet.write(row, col, float(result[header]), money)
                elif header in obj.quantity_fields:
                    sheet.write(row, col, row, numbers)
                else:
                    sheet.write(row, col, result[header], strings)
            else:
                sheet.write(row, col, None)
            col += 1
        row += 1

    return sheet


# build excel worksheet
def worksheets_generate(obj, workbook, file, ns):
    for key, value in obj.tags.items():

        worksheet = workbook.add_worksheet(name=key)

        # excel cell formatting
        bold = workbook.add_format({'bold': True})
        date = workbook.add_format({'num_format': 'dd/mm/yy'})
        money = workbook.add_format({'num_format': '#,##0.00'})
        numbers = workbook.add_format({'num_format': '0'})
        strings = workbook.add_format({'num_format': '@'})

        if key == 'KontoZapisRestructured':
            # process non existing table by specifying which table and tags it is based
            results = fast_iter(file, ns + 'KontoZapis')
            headers = get_headers(['LpZapisu',
                                   'NrZapisu',
                                   'KwotaWinien',
                                   'KwotaWinienWaluta',
                                   'KodWalutyWinien',
                                   'OpisZapisuWinien',
                                   'KwotaMa',
                                   'KwotaMaWaluta',
                                   'KodWalutyMa',
                                   'OpisZapisuMa'], results)
            headers.insert(2, 'KodKonta')
            results = change_data(results)

        else:
            results = fast_iter(file, ns + key)
            headers = get_headers(value, results)

        fill_sheet(headers, worksheet, results, obj, bold, date, money, numbers, strings)

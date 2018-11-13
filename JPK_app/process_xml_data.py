import lxml.etree as ET


# process xml elements to arrange them in an array (results) of dictionaries (result)
def process_elem(elem, results):
    result = {}
    for child in elem.iterchildren():
        result[child.tag[child.tag.index('}') + 1:]] = child.text
    results.append(result)


# iterate through xml structure Based on Liza Daly's fast_iter
# http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
def fast_iter(file_path, tag, *args, **kwargs):
    # tag is composed of namespace and table name
    context = ET.iterparse(file_path, events=('end',), tag=tag)
    results = []

    for event, elem in context:
        process_elem(elem, results)
        elem.clear()
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context
    return results


# get type of file (VAT, KR...) by reading the beginning of xml file in search of namespace tag
def get_ns(file_path):
    ns = ""

    with open(file_path, 'r') as f:
        start = f.read(200)
        if 'http://jpk.mf.gov.pl/wzor/2016/10/26/10261/' in start:
            ns = '{http://jpk.mf.gov.pl/wzor/2016/10/26/10261/}'
        elif 'http://jpk.mf.gov.pl/wzor/2016/03/09/03091/' in start:
            ns = '{http://jpk.mf.gov.pl/wzor/2016/03/09/03091/}'

    f.close()
    return ns


# create list of exel columns that are not empty
def get_headers(keys, results):
    headers = []
    for el in keys:
        # True for any tag that doesn't exist in result keys
        test_if_empty = len([True for result in results if el not in result.keys()])
        # append header to headers list if at least one row in a table contains a value for that header
        if test_if_empty != len(results):
            headers.append(el)
    return headers


# change parsing result in order to get KodKonta instead of KodKontaWinien/KodKontaMa with values in a single row - generic
def change_data_generic(result, required_elements, optional_elements):
    new_result = required_elements
    for el in optional_elements:
        if el in result.keys():
            new_result[el] = result[el]
    return new_result


# change parsing result in order to get KodKonta instead of KodKontaWinien/KodKontaMa with values in a single row - application
def change_data(results):
    new_results = []
    # match values from KontoZapis to KontoZapisRestructured
    for result in results:
        debit_elements = {
                'LpZapisu': result['LpZapisu'],
                'NrZapisu': result['NrZapisu'],
                'KodKonta': result['KodKontaWinien'],
                'KwotaWinien': result['KwotaWinien'],
                'KwotaMa': None,
                'OpisZapisuMa': None,
            }
        credit_elements = {
                'LpZapisu': result['LpZapisu'],
                'NrZapisu': result['NrZapisu'],
                'KodKonta': result['KodKontaMa'],
                'KwotaWinien': None,
                'OpisZapisuWinien': None,
                'KwotaMa': result['KwotaMa'],
            }
        debit_optional_elements = ['KwotaWinienWaluta', 'KodWalutyWinien', 'OpisZapisuWinien']
        credit_optional_elements = ['KwotaMaWaluta', 'KodWalutyMa', 'OpisZapisuMa']

        if result['KodKontaWinien'] not in [None, '-'] and result['KodKontaMa'] not in [None, '-']:

            new_result = change_data_generic(result, debit_elements, debit_optional_elements)
            new_results.append(new_result)

            new_result = change_data_generic(result, credit_elements, credit_optional_elements)
            new_results.append(new_result)

        elif result['KodKontaWinien'] not in [None, '-']:

            new_result = change_data_generic(result, debit_elements, debit_optional_elements)
            new_results.append(new_result)

        elif result['KodKontaMa'] not in [None, '-']:

            new_result = change_data_generic(result, credit_elements, credit_optional_elements)
            new_results.append(new_result)

    return new_results

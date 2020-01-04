# Templating using OpenPyXl to replace survey manager

import re 
import pathlib
import logging
from openpyxl import load_workbook

log = logging.getLogger(__name__)

def open_file(filePath):
    try:
        filePath = pathlib.Path(filePath).resolve(strict=True)
    except Exception as e:
        log.Error("Unable to resolve filePath: '{}'. {}".format(filePath, e))
        return None
    
    try:
        wb = load_workbook(filename=str(filePath))
    except Exception as e:
        log.Error("Unable to open workbook: '{}'. {}".format(filePath,e))
        return None
    
    return wb


def generate_template(wb):
    ranges = dict()
    meta = dict()

    for dn in wb.defined_names.definedName:
        
        tagCheck = re.sub('tags','',dn.name,flags=re.IGNORECASE)
        if dn.name in ranges.keys():
            raise AttributeError
        elif tagCheck in ranges.keys():
            ranges[tagCheck]['tagNamedRange'] = dn.name
            ranges[tagCheck]['tagRange'] = dn.attr_text
        else: 
            ranges[dn.name] = {"namedRange":dn.name, "range":dn.attr_text}
    
    return dict(ranges=ranges, meta=meta, wb=wb)


def load_from_workbook(wb, template):

    
    data = dict()
    for nr, details in template['ranges'].items():
        dataSheet, dataRange = details['range'].split('!')
        tagSheet, tagRange = details['tagRange'].split('!')

        loadData = {tagCell[0].value:dataCell[0].value for dataCell, tagCell in zip(wb[dataSheet][dataRange], wb[tagSheet][tagRange])}
        data[nr] = loadData

    return data

def write_to_workbook(template, data):
    wb = template['wb']

    for nr, details in template['ranges'].items():
        newData = data[nr]
        dataSheet, dataRange = details['range'].split('!')
        tagSheet, tagRange = details['tagRange'].split('!')

        for dataCell, tagCell in zip(wb[dataSheet][dataRange], wb[tagSheet][tagRange]):
            dataCell[0].value = newData[tagCell[0].value]
        
    return wb


def create_workbook_from_template(template, fname, outPath):

    outFile = pathlib.Path(outPath).resolve(strict=True).joinpath(fname)
    wb = template['wb']

    alternateData = {'Table1': {'CatA': 11, 'CatB': 12, 'CatC': 13}}
    newWorkBook = write_to_workbook(template,alternateData)

    newWorkBook.save(filename=str(outFile))
    print('Success. Worbook saved to: {}'.format(outFile))


def validate_workbook(wb, template):
    return generate_template(wb)['ranges'] == template['ranges']


def load_survey_data(filePath, template):

    if validate_workbook(filePath, template) == True:
        print('Workbook is valid {}'.format(filePath))
        return load_from_workbook(filePath, template)
    else:
        print('Workbook is NOT valid. {}'.format(filePath))
        return None
    



fPath = './BasicWorkbook.xlsx'
wb = open_file(fPath)
print('Generating Template... Done.')
tplt = generate_template(wb)

print('\n\nRead default values:')
data = load_from_workbook(wb, tplt)
print(data)

print('\n\nCreate new workbook from template:')
create_workbook_from_template(tplt,'Basic_8888888.xlsx','./')

print('\n\nLoad updated survey data:')
wb2 = open_file('./Basic_8888888.xlsx')
data2 = load_survey_data(wb2, tplt)
print(data2)

print('\n\nLoad edited workbook:')
wb3 = open_file('./BrokenWorkbook.xlsx')
data3 = load_survey_data(wb3, tplt)



"""Minimal synthetic OOXML fixture for reader/gate tests, with no private dependency.

This is a reader fixture, not a styled application workbook or an export test.
The real builder/updater must be checked separately with Codex's spreadsheet runtime.
"""
import zipfile
from xml.sax.saxutils import escape

HEADERS = ['Application ID','Company','Job title','Category','Priority','Status','Applied date','Advert URL','Location','Next action','Due date','First progressed date','Updated date','Notes','Requisition ID','Search match']

def write_fixture(path, records=()):
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    def row(number, values):
        cells=[]
        for i,value in enumerate(values):
            column=chr(65+i)
            if isinstance(value,(int,float)):
                cells.append(f'<c r="{column}{number}"><v>{value}</v></c>')
            else:
                cells.append(f'<c r="{column}{number}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
        return f'<row r="{number}">' + ''.join(cells) + '</row>'
    rows=[row(5,HEADERS)]+[row(n,[r.get(h,'') for h in HEADERS]) for n,r in enumerate(records,6)]
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('xl/workbook.xml',f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets><sheet name="Applications" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="{ns}"><sheetData>{"".join(rows)}</sheetData></worksheet>')

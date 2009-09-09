import re
import datetime

FRIENDLY_MAP = {'hr':'H.R.', 'hres':'H.RES.', 's':'S.', 'sres':'S.R.', 'hconres':'H.CON.RES.', 
    'sconres':'S.CON.RES.', 'hjres':'H.J.RES.', 'sjres':'S.J.RES.', 'hjr':'H.J.RES.', 'sjr':'S.J.RES.'}

GT_MAP = {'hr':'h', 'hres':'hr', 's':'s', 'sres':'sr', 'sjres':'sjr', 'hjres':'hjr'}

DOC_TYPE_MAP = {'cbo':'CBO CE', 'gao':'GAO', 'rpc':'RPC LN', 'dpc':'DPC LB', 'omb':'OMB Memo', 'srp':'RCR SRP', 'jct':'JCT', 'crs':'CRS', 'sap':'OMB SAP'}

TYPE_NAME_MAP = {'cbo':'CBO Cost Estimates', 'crs':'CRS Reports', 
                    'gao':'GAO Reports',
                    'rpc':'Republican Policy Committee Legislative Notices',
                    'dpc':'Democratic Policy Committee Reports and Briefs',
                    'omb':'OMB Memos', 'sap':'Statements of Administration Policy',
                    'srp':'Statements of Republican Policy',
                    'jct':'Joint Committee on Taxation Reports'}

def clean_bill_num(bill_num, space=False):
    bill_num = bill_num.replace(' ', '').replace('.', '').lower()
    p = re.compile('([a-z]{1,7})(\d{1,4})')
    m = p.match(bill_num)
    bill_type = FRIENDLY_MAP[m.group(1)]
    bill_num = m.group(2)
    spacer = ''
    if space: 
        spacer = ' '
    return "%s%s%s" % (bill_type, spacer, bill_num)
    
# return list of bill numbers extracted from string
def extract_legislation(haystack):
    haystack = haystack.upper()
    p = re.compile('S\.?\s?CON\.?\s?RES\.?\s?\d{1,5}|H\.?\s?CON\s?RES\.?\s?\d{1,5}|S\.?\s?J\.?\s?RES\.?\s\d{1,5}|H\.?\s?J\.?\s?RES\.?\s\d{1,5}|S\.?\s?RES\.?\s?\d{1,5}|H\.?\s?RES\.?\s?\d{1,5}|H\.?\s?\R\.?\s?\d{1,5}|S\.?\s?\d{1,5}')
    needle_list = p.findall(haystack)
    for i in range(len(needle_list)):
        needle_list[i] = clean_bill_num(needle_list[i])
    return needle_list
    
#returns number of Congress in session for provided year
def congress_from_year(year):
    if year < 1789:
        return None
    else:
        return int((year-1789)/2) + 1
               
#returns session number of Congress for a provided year        
def session_from_year(year):
    return 2 - (year % 2)
    
#returns dict contaning congress number and session number for a given year
def congress_session_from_year(year):
    congress = congress_from_year(year)
    session = session_from_year(year)
    return {'congress':congress, 'session':session}
    
#returns dict containing congress number and session number for current year
def current_congress_session():
    return congress_session_from_year(datetime.datetime.now().year)
    
def int_to_ordinal(num):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

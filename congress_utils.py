import re

# return list of bill numbers extracted from string
def extract_legislation(haystack):
    haystack = haystack.upper()
    p = re.compile('S\.?\s?CON\.?\s?RES\.?\s?\d{1,5}|H\.?\s?CON\s?RES\.?\s?\d{1,5}|S\.?\s?J\.?\s?RES\.?\s\d{1,5}|H\.?\s?J\.?\s?RES\.?\s\d{1,5}|S\.?\s?RES\.?\s?\d{1,5}|H\.?\s?RES\.?\s?\d{1,5}|H\.?\s?\R\.?\s?\d{1,5}|S\.?\s?\d{1,5}')
    needle_list = p.findall(haystack)
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
from bs4 import BeautifulSoup, Tag
import httpx as h
from tabulate import tabulate

r = h.get('https://www.naqt.com/stats/school/players.jsp?org_id=69304')

html = BeautifulSoup(r.text, 'lxml')

tbl = html.find('section', attrs={'id': 'players'}).table

headers = [e.text for e in tbl.thead.tr.find_all('th')]

data = []

elem: Tag
for elem in tbl.tbody.find_all('tr'):
    temp = []
    for z in elem.find_all():
        temp.append(z.text)
    data.append(temp[1:])

print(tabulate(data, headers, showindex=False))

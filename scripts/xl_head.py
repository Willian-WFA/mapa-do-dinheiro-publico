import zipfile, sys
from xml.etree import ElementTree as ET
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def head(path, sheet_idx, maxrows=40, maxss=6000):
    z = zipfile.ZipFile(path)
    wbx = ET.fromstring(z.read('xl/workbook.xml'))
    names = [s.get('name') for s in wbx.find(NS + 'sheets')]
    ss = []
    with z.open('xl/sharedStrings.xml') as f:
        for ev, el in ET.iterparse(f):
            if el.tag == NS + 'si':
                ss.append(''.join(t.text or '' for t in el.iter(NS + 't')))
                el.clear()
                if len(ss) >= maxss:
                    break
    rows = []
    with z.open(f'xl/worksheets/sheet{sheet_idx + 1}.xml') as f:
        for ev, el in ET.iterparse(f):
            if el.tag == NS + 'row':
                r = []
                for c in el.findall(NS + 'c'):
                    v = c.find(NS + 'v')
                    if v is None:
                        continue
                    if c.get('t') == 's':
                        i = int(v.text)
                        r.append(ss[i] if i < len(ss) else f'<ss{i}>')
                    else:
                        r.append(v.text)
                rows.append(r)
                el.clear()
                if len(rows) >= maxrows:
                    break
    return names, rows


if __name__ == '__main__':
    n, r = head(sys.argv[1], int(sys.argv[2]))
    print(n[:15])
    for x in r[:int(sys.argv[3]) if len(sys.argv) > 3 else 20]:
        print(x[:10])

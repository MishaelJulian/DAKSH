import json
import re
from bs4 import BeautifulSoup

sample_daily_status = """
<div id="caseBusinessDiv_caseType">
  <div id="mydiv" align="center">
    <span><h1>Daily Status</h1></span>
    <center>
      <span>PRL. CITY CIVIL AND SESSIONS JUDGE</span>
    </center>
    <center>
      <span><b>In the court of</b>:CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE</span>
    </center>
    <center>
      <span><b>CNR Number</b>:KABC010342242022</span>
    </center>
    <center>
      <span><b>Case Number</b>:EX/0000002/2023</span>
    </center>
    <center>
      <span>KRISHNAMURTHY G <b>versus</b> SATHISH M</span>
    </center>
    <center>
      <span><b>Date</b>: 06-12-2025</span>
    </center>
    <center>
      <table border="0" width="87%">
        <tbody>
          <tr>
            <td align="left" width="25%"><b>Business</b></td>
            <td width="1%">:</td>
            <td align="left" width="69%">An IA.No.III filed by the JDR is dismissed. The memo filed by the DHR is hereby allowed and E.P is closed as fully satisfied.<br/></td>
          </tr>
          <tr>
            <td align="left" width="25%"><b>Nature of Disposal</b></td>
            <td width="1%">:</td>
            <td align="left" width="69%">DISMISSED<br/></td>
          </tr>
          <tr>
            <td align="left" width="25%"><b>Disposal Date</b></td>
            <td width="1%">:</td>
            <td align="left" width="69%">06-12-2025<br/></td>
          </tr>
          <tr>
            <td align="right" colspan="3">CCH64 LXIII ADDL. CITY CIVIL AND SESSIONS JUDGE</td>
          </tr>
        </tbody>
      </table>
    </center>
  </div>
</div>
"""

soup = BeautifulSoup(sample_daily_status, 'html.parser')

def parse_daily_status_dom(soup):
    def clean(t):
        return ' '.join(t.strip().split()) if t else ''

    record = {
        'establishment': None,
        'judge': None,
        'cnr': None,
        'case_number': None,
        'case_title': None,
        'date': None,
        'business': None,
        'next_purpose': None,
        'next_hearing_date': None,
        'nature_of_disposal': None,
        'disposal_date': None,
        'signing_judge': None
    }
    
    # Parse center/span lines
    for span in soup.find_all('span'):
        txt = clean(span.get_text())
        if not txt or 'daily status' in txt.lower():
            continue
        if re.search(r'in the court of\s*:', txt, re.IGNORECASE):
            record['judge'] = re.sub(r'^.*in the court of\s*:\s*', '', txt, flags=re.IGNORECASE).strip()
        elif re.search(r'cnr number\s*:', txt, re.IGNORECASE):
            record['cnr'] = re.sub(r'^.*cnr number\s*:\s*', '', txt, flags=re.IGNORECASE).strip()
        elif re.search(r'case number\s*:', txt, re.IGNORECASE):
            record['case_number'] = re.sub(r'^.*case number\s*:\s*', '', txt, flags=re.IGNORECASE).strip()
        elif re.search(r'date\s*:', txt, re.IGNORECASE):
            record['date'] = re.sub(r'^.*date\s*:\s*', '', txt, flags=re.IGNORECASE).strip()
        elif 'versus' in txt.lower() or ' vs ' in txt.lower():
            record['case_title'] = txt
        elif not record['establishment'] and not any(k in txt.lower() for k in ['court', 'cnr', 'case', 'date', 'versus', 'vs']):
            record['establishment'] = txt

    # Parse table rows
    table = soup.find('table')
    if table:
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 3:
                lbl = clean(tds[0].get_text()).lower().replace(':', '')
                val = clean(tds[2].get_text())
                if 'business' in lbl:
                    record['business'] = val
                elif 'next purpose' in lbl:
                    record['next_purpose'] = val
                elif 'next hearing date' in lbl:
                    record['next_hearing_date'] = val
                elif 'nature of disposal' in lbl:
                    record['nature_of_disposal'] = val
                elif 'disposal date' in lbl:
                    record['disposal_date'] = val
            elif len(tds) == 1 and tds[0].get('colspan') == '3':
                record['signing_judge'] = clean(tds[0].get_text())
                if not record['judge']:
                    record['judge'] = record['signing_judge']
                    
    return record

rec = parse_daily_status_dom(soup)
print(json.dumps(rec, indent=2))

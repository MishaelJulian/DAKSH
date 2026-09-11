from html.parser import HTMLParser

class HeadingSiblingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.current_heading = None
        self.in_heading = False
        
        self.capture_depth = 0
        self.captured_html = ""
        self.in_table = False
        self.in_ul = False
        self.current_table = None
        self.current_ul = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ['h3', 'h4', 'h5', 'h6'] or ('class' in attrs_dict and 'h2class' in attrs_dict['class']):
            self.in_heading = True
            self.current_heading = {
                'tag': tag,
                'class': attrs_dict.get('class'),
                'id': attrs_dict.get('id'),
                'text': '',
                'following_tables': [],
                'following_uls': []
            }
        elif self.current_heading is not None:
            if tag == 'table':
                self.current_table = {
                    'id': attrs_dict.get('id'),
                    'class': attrs_dict.get('class'),
                    'rows': [],
                    'current_row': []
                }
                self.in_table = True
            elif tag == 'ul':
                self.current_ul = {
                    'class': attrs_dict.get('class'),
                    'items': [],
                    'current_item': ''
                }
                self.in_ul = True
            elif tag == 'tr' and self.in_table:
                self.current_table['current_row'] = []
            elif tag in ['td', 'th'] and self.in_table:
                self.in_cell = True
                self.cell_data = ""
            elif tag == 'li' and self.in_ul:
                self.in_li = True
                self.li_data = ""

    def handle_endtag(self, tag):
        if tag in ['h3', 'h4', 'h5', 'h6'] or self.in_heading:
            if self.in_heading:
                self.headings.append(self.current_heading)
                self.in_heading = False
        elif self.current_heading is not None:
            if tag == 'table' and self.in_table:
                self.current_heading['following_tables'].append(self.current_table)
                self.current_table = None
                self.in_table = False
            elif tag == 'ul' and self.in_ul:
                self.current_heading['following_uls'].append(self.current_ul)
                self.current_ul = None
                self.in_ul = False
            elif tag == 'tr' and self.in_table:
                self.current_table['rows'].append(self.current_table['current_row'])
            elif tag in ['td', 'th'] and self.in_table:
                if hasattr(self, 'cell_data'):
                    self.current_table['current_row'].append(self.cell_data.strip())
                    del self.cell_data
            elif tag == 'li' and self.in_ul:
                if hasattr(self, 'li_data'):
                    self.current_ul['items'].append(self.li_data.strip())
                    del self.li_data

    def handle_data(self, data):
        if self.in_heading:
            self.current_heading['text'] += data
        elif self.in_table:
            if hasattr(self, 'cell_data'):
                self.cell_data += data
        elif self.in_ul:
            if hasattr(self, 'li_data'):
                self.li_data += data

def main():
    with open('logs/after_return_attempt_2.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = HeadingSiblingParser()
    parser.feed(html)

    # Print only headings related to case details page
    relevant_headings = ["case details", "case status", "petitioner", "respondent", "acts", "processes", "history", "orders", "transfer"]
    
    for h in parser.headings:
        text = h['text'].strip()
        text_lower = text.lower()
        if any(rh in text_lower for rh in relevant_headings):
            print(f"\n================ HEADING: '{text}' ================")
            print(f"Tag: {h['tag']}, Class: {h['class']}, ID: {h['id']}")
            
            for idx, t in enumerate(h['following_tables'][:1]): # Print first following table
                print(f"  Table {idx}: ID={t['id']}, Class={t['class']}")
                print(f"  Rows count: {len(t['rows'])}")
                for r_idx, r in enumerate(t['rows'][:5]):
                    print(f"    Row {r_idx}: {r}")
                    
            for idx, u in enumerate(h['following_uls']):
                print(f"  UL {idx}: Class={u['class']}")
                print(f"  Items: {u['items']}")

if __name__ == '__main__':
    main()

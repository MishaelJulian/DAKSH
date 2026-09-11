import re
from html.parser import HTMLParser

class DetailsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.current_tag = None
        self.in_heading = False
        self.heading_text = ""
        self.tables = []
        self.current_table = None
        self.row_count = 0
        self.headings = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tags.append(tag)
        self.current_tag = tag
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or 'class' in attrs_dict and 'h2class' in attrs_dict['class']:
            self.in_heading = True
            self.heading_text = ""
        if tag == 'table':
            self.current_table = {
                'id': attrs_dict.get('id'),
                'class': attrs_dict.get('class'),
                'headers': [],
                'rows': []
            }
            self.row_count = 0
        if tag == 'tr' and self.current_table is not None:
            self.row_count += 1
            self.current_table['rows'].append([])
        if tag in ['td', 'th'] and self.current_table is not None:
            pass

    def handle_endtag(self, tag):
        if self.tags:
            self.tags.pop()
        self.current_tag = self.tags[-1] if self.tags else None
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or self.in_heading:
            if self.in_heading:
                self.headings.append(self.heading_text.strip())
                self.in_heading = False
        if tag == 'table' and self.current_table is not None:
            self.tables.append(self.current_table)
            self.current_table = None

    def handle_data(self, data):
        if self.in_heading:
            self.heading_text += data
        if self.current_table is not None and self.current_table['rows']:
            # Append text to the last cell of the last row
            row = self.current_table['rows'][-1]
            cleaned = data.strip().replace('\xa0', ' ')
            if cleaned:
                row.append(cleaned)

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = DetailsParser()
    parser.feed(html)

    print("--- HEADINGS ---")
    for h in parser.headings:
        if h:
            print("-", h)

    print("\n--- TABLES SUMMARY ---")
    for idx, t in enumerate(parser.tables):
        print(f"\nTable {idx}: ID={t['id']}, Class={t['class']}")
        print(f"Row count: {len(t['rows'])}")
        # Print first few rows
        for r_idx, r in enumerate(t['rows'][:5]):
            print(f"  Row {r_idx}: {r}")

if __name__ == '__main__':
    main()

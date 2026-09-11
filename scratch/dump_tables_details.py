from html.parser import HTMLParser

class DumpParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current_table = None
        self.current_row = None
        self.current_cell = ""
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'table':
            self.current_table = {
                'id': attrs_dict.get('id'),
                'class': attrs_dict.get('class'),
                'rows': []
            }
        elif tag == 'tr' and self.current_table is not None:
            self.current_row = []
            self.current_table['rows'].append(self.current_row)
        elif tag in ['td', 'th'] and self.current_row is not None:
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if tag == 'table' and self.current_table is not None:
            self.tables.append(self.current_table)
            self.current_table = None
        elif tag == 'tr':
            self.current_row = None
        elif tag in ['td', 'th'] and self.in_cell:
            self.in_cell = False
            if self.current_row is not None:
                self.current_row.append(self.current_cell.strip())

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = DumpParser()
    parser.feed(html)

    print(f"Found {len(parser.tables)} tables")
    for idx, t in enumerate(parser.tables):
        print(f"\n================ TABLE {idx} ================")
        print(f"ID: {t['id']}, Class: {t['class']}")
        print(f"Rows ({len(t['rows'])} total):")
        for r_idx, r in enumerate(t['rows'][:15]):
            print(f"  Row {r_idx}: {r}")
        if len(t['rows']) > 15:
            print(f"  ... and {len(t['rows']) - 15} more rows")

if __name__ == '__main__':
    main()

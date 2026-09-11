from html.parser import HTMLParser

class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.in_heading = False
        self.current_heading = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or ('class' in attrs_dict and 'h2class' in attrs_dict['class']):
            self.in_heading = True
            self.current_heading = ""

    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or self.in_heading:
            if self.in_heading:
                self.headings.append(self.current_heading.strip())
                self.in_heading = False

    def handle_data(self, data):
        if self.in_heading:
            self.current_heading += data

def main():
    with open('logs/after_return_attempt_2.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = HeadingParser()
    parser.feed(html)

    print("All headings in after_return_attempt_2.html:")
    for h in parser.headings:
        if h:
            print("-", h)

if __name__ == '__main__':
    main()

from html.parser import HTMLParser

class DetailContainerLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_detail_container = False
        self.div_depth = 0
        self.links = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div':
            div_id = attrs_dict.get('id') or ''
            if div_id.startswith('CS') or self.in_detail_container:
                if not self.in_detail_container:
                    self.in_detail_container = True
                    self.div_depth = 1
                    print(f"Entered detail container div ID: {div_id}")
                else:
                    self.div_depth += 1
        
        if self.in_detail_container:
            if tag == 'a':
                self.current_link = dict(attrs)
                self.current_link['text'] = ""

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_detail_container:
            self.div_depth -= 1
            if self.div_depth == 0:
                self.in_detail_container = False
                print("Exited detail container div")
                
        if tag == 'a' and self.in_detail_container and self.current_link is not None:
            self.links.append(self.current_link)
            self.current_link = None

    def handle_data(self, data):
        if self.in_detail_container and self.current_link is not None:
            self.current_link['text'] += data

def main():
    with open('logs/after_return_attempt_2.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = DetailContainerLinkParser()
    parser.feed(html)

    print(f"\nFound {len(parser.links)} links inside detail container:")
    for idx, link in enumerate(parser.links):
        text_safe = link['text'].strip().encode('ascii', errors='ignore').decode('ascii')
        onclick_safe = (link.get('onclick') or '').encode('ascii', errors='ignore').decode('ascii')
        href_safe = (link.get('href') or '').encode('ascii', errors='ignore').decode('ascii')
        print(f"Link {idx}: text='{text_safe}', href='{href_safe}', onclick='{onclick_safe}', class='{link.get('class')}'")

if __name__ == '__main__':
    main()

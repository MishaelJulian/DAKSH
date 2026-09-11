from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current_link = dict(attrs)
            self.current_link['text'] = ""

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_link is not None:
            self.links.append(self.current_link)
            self.current_link = None

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link['text'] += data

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()

    parser = LinkParser()
    parser.feed(html)

    print(f"Total links: {len(parser.links)}")
    
    # Filter for relevant links
    relevant_links = []
    for link in parser.links:
        onclick = link.get('onclick') or ''
        href = link.get('href') or ''
        text = link.get('text') or ''
        
        # Check for case/order details, history, etc.
        if 'viewHistory' in onclick or 'displayPdf' in onclick or 'history' in href or 'pdf' in href or 'order' in onclick.lower() or 'history' in onclick.lower():
            relevant_links.append(link)
            
    print(f"Relevant links: {len(relevant_links)}")
    for idx, link in enumerate(relevant_links):
        text_safe = link['text'].strip().encode('ascii', errors='ignore').decode('ascii')
        onclick_safe = (link.get('onclick') or '').encode('ascii', errors='ignore').decode('ascii')
        href_safe = (link.get('href') or '').encode('ascii', errors='ignore').decode('ascii')
        print(f"Link {idx}: text='{text_safe}', href='{href_safe}', onclick='{onclick_safe}'")

if __name__ == '__main__':
    main()

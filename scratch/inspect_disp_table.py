import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Search for id="dispTable" and print 500 characters before it
    match = re.search(r'<table[^>]*id="dispTable"', html)
    if match:
        print("Found dispTable!")
        start = match.start()
        parent_start = max(0, start - 1000)
        print("Surrounding parent context for dispTable:")
        print(html[parent_start:start])
    else:
        print("dispTable not found.")

if __name__ == '__main__':
    main()

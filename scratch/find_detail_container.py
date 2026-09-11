import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Search for case_details_table and see the surrounding HTML tags.
    # We want to trace upwards to find the container div ID/class.
    match = re.search(r'<table[^>]*class="[^"]*case_details_table[^"]*"', html)
    if match:
        print("Found case_details_table!")
        start = match.start()
        # Print 1500 characters before the table to see its parent divs
        parent_start = max(0, start - 1500)
        print("Surrounding parent context:")
        print(html[parent_start:start])
    else:
        print("case_details_table not found.")

if __name__ == '__main__':
    main()

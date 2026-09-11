import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Find all tables
    table_matches = list(re.finditer(r'<table[^>]*>', html, re.IGNORECASE))
    print(f"Total tables found: {len(table_matches)}")
    
    # For each table, extract its inner content or headers
    for idx, match in enumerate(table_matches):
        start = match.start()
        # Find closing </table>
        end_match = html.find('</table>', start)
        if end_match != -1:
            table_html = html[start:end_match + 8]
        else:
            table_html = html[start:start + 1000]
            
        print(f"\n--- TABLE {idx} ---")
        print("Tag:", html[start:html.find('>', start)+1])
        # Print first 300 characters of the table HTML
        print("Snippet:", table_html[:400].replace('\n', ' ').strip())
        print("Snippet End:", table_html[-200:].replace('\n', ' ').strip() if len(table_html) > 400 else "")

if __name__ == '__main__':
    main()

import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("Total length:", len(html))
    
    # Find all div tags and their IDs and classes
    div_pattern = re.compile(r'<div\s+([^>]*id="[^"]+"[^>]*)>')
    divs = div_pattern.findall(html)
    print("=== Divs with IDs ===")
    for d in divs[:50]:
        print(d)
        
    # Find all table tags and their IDs and classes
    table_pattern = re.compile(r'<table\s+([^>]*id="[^"]+"[^>]*)>')
    tables = table_pattern.findall(html)
    print("=== Tables with IDs ===")
    for t in tables:
        print(t)
        
    # Find if there are divs/tables containing any case details like names
    # Let's search for some case details, for example MURUDESHWAR or MURUDESHWAR CERAMICS
    print("=== Searches for specific text ===")
    for word in ["MURUDESHWAR", "EX/1/2010"]:
        count = 0
        for match in re.finditer(re.escape(word), html, re.IGNORECASE):
            count += 1
            start = max(0, match.start() - 250)
            end = min(len(html), match.end() + 250)
            print(f"Occurrence {count} of '{word}':")
            print(html[start:end])
            print("-" * 50)

if __name__ == '__main__':
    main()

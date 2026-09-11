import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Search for viewHistory function javascript definition
    match = re.search(r'function\s+viewHistory\s*\(', html)
    if match:
        print("Found function viewHistory!")
        start = match.start()
        end = min(len(html), start + 2000)
        print(html[start:end])
    else:
        print("function viewHistory not found in HTML.")
        
    # Let's also look for AJAX / post calls in component JS or scripts
    # Find all script blocks
    script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(html)
    print(f"Found {len(scripts)} script blocks.")
    for idx, s in enumerate(scripts):
        if "viewHistory" in s or "view_history" in s or "showListTable" in s or "dispTable" in s:
            print(f"--- Script {idx} containing keywords ---")
            print(s[:1500])
            print("---------------------------------------")

if __name__ == '__main__':
    main()

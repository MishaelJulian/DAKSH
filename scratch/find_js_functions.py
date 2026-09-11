import re

def main():
    # Let's search inside logs/after_return_attempt_2.html
    try:
        with open('logs/after_return_attempt_2.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        with open('logs/after_view.html', 'r', encoding='utf-8') as f:
            html = f.read()

    # Search for script tags containing viewBusiness
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    print(f"Found {len(scripts)} script tags in HTML.")
    
    found = False
    for idx, script in enumerate(scripts):
        if 'viewBusiness' in script:
            print(f"\n=== Script {idx} containing viewBusiness ===")
            found = True
            # Let's extract the function definition
            match = re.search(r'function\s+viewBusiness\s*\(.*?\)\s*\{.*?\}', script, re.DOTALL)
            if match:
                print(match.group(0))
            else:
                # Print lines containing viewBusiness
                lines = script.splitlines()
                for line_no, line in enumerate(lines):
                    if 'viewBusiness' in line:
                        print(f"{line_no}: {line}")
                        
    if not found:
        print("viewBusiness not found in inline scripts. It might be in an external .js file.")
        # Search for external js files in script src attributes
        srcs = re.findall(r'<script[^>]*src=["\'](.*?)["\']', html, re.IGNORECASE)
        print("External script sources:")
        for src in srcs:
            print("-", src)

if __name__ == '__main__':
    main()

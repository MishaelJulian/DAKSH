import re

def main():
    with open('logs/after_view.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Search for "Petitioner and Advocate"
    pattern = re.compile(r'Petitioner\s+and\s+Advocate', re.IGNORECASE)
    matches = list(pattern.finditer(html))
    print(f"Matches found: {len(matches)}")
    for i, m in enumerate(matches):
        start = max(0, m.start() - 200)
        end = min(len(html), m.end() + 2000)
        print(f"\n--- MATCH {i} ---")
        print(html[start:end])

if __name__ == '__main__':
    main()

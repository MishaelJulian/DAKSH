"""Diagnostic script inspecting 2010 log HTML files."""
from __future__ import annotations
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    print("=== Inspecting 2010 Run HTML Snapshots ===")
    with open("logs/after_return_attempt_1.html", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    print(f"File length: {len(content)} bytes")
    # Find form elements
    forms = re.findall(r'<form[^>]*>', content)
    print(f"Forms found ({len(forms)}):")
    for f in forms[:5]:
        print(f"  {f}")

    # Find hidden inputs
    inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', content)
    print(f"\nHidden inputs found ({len(inputs)}):")
    for i in inputs[:10]:
        print(f"  {i}")

    # Find script src attributes
    scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', content)
    print(f"\nScript sources ({len(scripts)}):")
    for s in scripts[:10]:
        print(f"  {s}")

if __name__ == "__main__":
    main()

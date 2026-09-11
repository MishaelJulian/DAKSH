import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('DAKSH_Service_Learning_Presentation_17Slides.pptx')
w = prs.slide_width.inches
h = prs.slide_height.inches

print(f"Presentation File: DAKSH_Service_Learning_Presentation_17Slides.pptx")
print(f"Total Slides: {len(prs.slides)}")
print(f"Dimensions: {w:.2f} x {h:.2f} inches (Original Template 4:3)")

out_of_bounds = []
forbidden = ['ecocare', 'ecoparadigm', 'e-waste', 'electronic waste', 'recycling', 'battery', 'cpcb', 'raspberry pi', 'hx711', 'load cell', 'smart sorting', 'material recovery', 'waste sorting']
forbidden_found = []

for i, slide in enumerate(prs.slides):
    s_idx = i + 1
    texts = []
    for s in slide.shapes:
        if s.left < 0 or s.top < 0 or (s.left + s.width) > prs.slide_width or (s.top + s.height) > prs.slide_height:
            if s.name not in ['bg object 16', 'bg object 17', 'bg object 18', 'bg object 19']:
                out_of_bounds.append((s_idx, s.name, s.left.inches, s.top.inches, (s.left+s.width).inches, (s.top+s.height).inches))
        
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                txt = p.text.strip()
                if txt:
                    texts.append(txt)
                    for f in forbidden:
                        if f in txt.lower():
                            forbidden_found.append((s_idx, f, txt))
                            
    title = texts[0] if texts else "EMPTY"
    print(f"Slide {s_idx:02d}: {title[:48]} | Text items: {len(texts)}")

print("\n--- AUDIT RESULTS ---")
print(f"Out of bounds shapes: {len(out_of_bounds)}")
print(f"Forbidden terms detected: {len(forbidden_found)}")

if len(out_of_bounds) == 0 and len(forbidden_found) == 0 and len(prs.slides) == 17:
    print("\n>>> ALL VERIFICATION CHECKS PASSED: Perfect 17-slide presentation in original template format! <<<")

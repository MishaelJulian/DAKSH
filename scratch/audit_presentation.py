import pptx
import sys

prs = pptx.Presentation('DAKSH_Service_Learning_Presentation.pptx')
print(f"Total slides: {len(prs.slides)}")

forbidden = [
    'ecocare', 'ecoparadigm', 'e-waste', 'electronic waste', 'recycling', 
    'battery', 'cpcb', 'raspberry pi', 'hx711', 'load cell', 'smart sorting', 
    'material recovery', 'waste sorting', 'ashutosh', 'bhavyasree', 'sohini', 'sudanshu'
]

forbidden_found = False

for idx, slide in enumerate(prs.slides):
    slide_num = idx + 1
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                t = p.text.strip()
                if t:
                    texts.append(t)
                    # Check forbidden
                    for f in forbidden:
                        if f in t.lower():
                            print(f"[ALERT] Slide {slide_num} contains forbidden word '{f}': \"{t}\"")
                            forbidden_found = True
                            
    title = texts[0] if texts else "EMPTY"
    print(f"Slide {slide_num}: {title[:45]} | Total text blocks: {len(texts)}")

if not forbidden_found:
    print("\n>>> SUCCESS: Zero forbidden or e-waste keywords found across all 28 slides! <<<")
else:
    print("\n>>> WARNING: Forbidden keywords were detected. Fix required. <<<")

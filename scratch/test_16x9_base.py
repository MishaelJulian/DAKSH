import pptx
from pptx.util import Inches, Pt

prs = pptx.Presentation('SamplePPT.pptx')
print("Original size:", prs.slide_width.inches, prs.slide_height.inches)

# Set slide width and height to 16:9
prs.slide_width = Inches(13.333333)
prs.slide_height = Inches(7.5)

print("New size:", prs.slide_width.inches, prs.slide_height.inches)

# Test saving to a test file
prs.save('scratch/test_16x9_base.pptx')
print("Saved scratch/test_16x9_base.pptx successfully!")

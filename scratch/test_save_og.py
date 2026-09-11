import pptx
import os

try:
    prs = pptx.Presentation('SamplePPT.pptx')
    prs.save('DAKSH_Service_Learning_Presentation.pptx')
    print("Successfully saved to DAKSH_Service_Learning_Presentation.pptx!")
except Exception as e:
    print("Error saving:", e)

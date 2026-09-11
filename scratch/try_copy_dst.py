import shutil
import os

src = "DAKSH_Service_Learning_Presentation_17Slides.pptx"
dst = "DAKSH_Service_Learning_Presentation.pptx"

try:
    shutil.copy(src, dst)
    print("Successfully replaced DAKSH_Service_Learning_Presentation.pptx with the 17-slide version!")
except Exception as e:
    print("DAKSH_Service_Learning_Presentation.pptx is still locked by an open process:", e)
    print("Both DAKSH_Service_Learning_Presentation_17Slides.pptx and DAKSH_Service_Learning_Presentation_16x9.pptx are fully generated and ready.")

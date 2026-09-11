import pptx
import os

prs = pptx.Presentation('SamplePPT.pptx')
print("Slide masters count:", len(prs.slide_masters))
print("Slide layouts in presentation:")
for idx, layout in enumerate(prs.slide_layouts):
    print(f"  Layout {idx}: '{layout.name}'")

# Extract all images from SamplePPT.pptx to inspect what images exist (logos, headers, etc.)
os.makedirs('scratch/extracted_images', exist_ok=True)
img_count = 0
for s_idx, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            img = shape.image
            img_bytes = img.blob
            ext = img.ext
            img_count += 1
            fname = f"scratch/extracted_images/slide_{s_idx+1}_{shape.name.replace(' ', '_')}.{ext}"
            with open(fname, 'wb') as f:
                f.write(img_bytes)
            print(f"Saved {fname} (size {len(img_bytes)} bytes, dims: {img.size})")

print(f"Total images extracted: {img_count}")

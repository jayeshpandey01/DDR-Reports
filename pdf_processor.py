import fitz
import os
import json

def extract_pdf_content(pdf_path, output_image_dir, doc_type=""):
    """Extracts text and images from a given PDF."""
    os.makedirs(output_image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    extracted_data = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        
        images_on_page = []
        # Get images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            # Optimization: Filter out tiny images (like lines, dots, or small icons) to save tokens and layout space
            if base_image["width"] < 150 or base_image["height"] < 150:
                continue
                
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{doc_type}_page{page_num+1}_img{img_index+1}.{image_ext}"
            image_filepath = os.path.join(output_image_dir, image_filename)
            
            with open(image_filepath, "wb") as image_file:
                image_file.write(image_bytes)
                
            images_on_page.append({
                "filename": image_filepath,
                "xref": xref
            })
            
        extracted_data.append({
            "page": page_num + 1,
            "text": text,
            "images": [img["filename"] for img in images_on_page]
        })
        
    return extracted_data

if __name__ == "__main__":
    # Test script locally
    sample_data = extract_pdf_content("Sample Report.pdf", "extracted_images", "sample")
    thermal_data = extract_pdf_content("Thermal Images.pdf", "extracted_images", "thermal")
    print(f"Extracted {len(sample_data)} pages from Sample Report.")
    print(f"Extracted {len(thermal_data)} pages from Thermal Images.")

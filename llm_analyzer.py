import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv(override=True)

# --- Pydantic Schema ---

class Introduction(BaseModel):
    Background: str
    Objective: str
    Scope_of_Work: str
    Tools_Used: str

class Metadata(BaseModel):
    Report_ID: str
    Site_Address: str
    Type_of_Structure: str
    Property_Type: str
    Floors: str
    Year_of_Construction: str
    Age_Building_years: str
    Inspection_Date: str
    Inspector_Names: str
    Customer_Name: str
    Customer_Mobile: str
    Customer_Email: str

class ConditionStat(BaseModel):
    Label: str
    Value: str

class SummarySection(BaseModel):
    Checklists_Flagged: str
    Score_Percentage: str
    Condition_Stats: list[ConditionStat]

class AreaDetail(BaseModel):
    Area: str
    Negative_Side_Inputs: str
    Positive_Side_Inputs: str
    Associated_Images: list[str]

class ChecklistItem(BaseModel):
    Question: str
    Value: str

class ChecklistCategory(BaseModel):
    Category_Name: str
    Score_Percentage: str
    Items: list[ChecklistItem]

class SummaryMapping(BaseModel):
    Impacted_Area: str
    Observed_Issue: str
    Probable_Cause: str
    Severity: str
    Suggested_Remedy: str

class DDRReport(BaseModel):
    Table_of_Contents: list[str]
    Introduction: Introduction
    Metadata: Metadata
    Summary: SummarySection
    Impacted_Areas: list[AreaDetail]
    Checklists: list[ChecklistCategory]
    Final_Summary_Table: list[SummaryMapping]
    Overall_Recommendations: list[str]
    Limitation_and_Precaution: str


def _separate_images(report_data):
    """Post-process: split Associated_Images into Normal_Images and Thermal_Images based on filename prefix."""
    if not report_data or "Impacted_Areas" not in report_data:
        return report_data
    
    for area in report_data["Impacted_Areas"]:
        all_images = area.get("Associated_Images", [])
        normal = []
        thermal = []
        for img in all_images:
            basename = os.path.basename(img).lower()
            if basename.startswith("thermal"):
                thermal.append(img)
            else:
                normal.append(img)
        area["Normal_Images"] = normal
        area["Thermal_Images"] = thermal
        del area["Associated_Images"]
    
    return report_data


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=30))
def analyze_with_gemini(sample_data, thermal_data):
    """Sends extracted text and images to Gemini for Checklist-styled JSON extraction."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return None
        
    client = genai.Client(api_key=api_key)
    
    # Build the text with clear separation of sample vs thermal images
    combined_text = "=== INSPECTION REPORT (Sample Report) ===\n"
    all_sample_images = []
    for page in sample_data:
        combined_text += f"\n-- Page {page['page']} --\n{page['text']}\n"
        if page['images']:
            # Only list the basenames for clarity
            img_basenames = [os.path.basename(img) for img in page['images']]
            combined_text += f"   [Sample Images on this page: {', '.join(img_basenames)}]\n"
            all_sample_images.extend(page['images'])
    
    combined_text += "\n\n=== THERMAL REPORT ===\n"
    all_thermal_images = []
    for page in thermal_data:
        combined_text += f"\n-- Page {page['page']} --\n{page['text']}\n"
        if page['images']:
            img_basenames = [os.path.basename(img) for img in page['images']]
            combined_text += f"   [Thermal Images on this page: {', '.join(img_basenames)}]\n"
            all_thermal_images.extend(page['images'])

    # Provide an image inventory to the LLM
    combined_text += f"\n\n=== IMAGE INVENTORY ===\n"
    combined_text += f"Total Sample/Normal Images: {len(all_sample_images)}\n"
    combined_text += f"Total Thermal Images: {len(all_thermal_images)}\n"

    # Group sample images by page for easy reference
    from collections import defaultdict
    page_images = defaultdict(list)
    for img in all_sample_images:
        basename = os.path.basename(img)
        # Extract page number from filename like "sample_page3_img1.jpeg"
        parts = basename.split("_")
        for p in parts:
            if p.startswith("page"):
                page_images[p].append(basename)
                break
    
    combined_text += "\nSample Images grouped by page:\n"
    for page_key in sorted(page_images.keys(), key=lambda x: int(x.replace("page","")) if x.replace("page","").isdigit() else 0):
        combined_text += f"  {page_key}: {', '.join(page_images[page_key])}\n"

    system_prompt = """You are an expert structural and thermal building inspector AI. Your job is to extract structured data from building inspection reports. Analyze the provided text carefully and fill every field accurately.

=== FIELD-BY-FIELD EXTRACTION GUIDE ===

### Table_of_Contents
Reconstruct the full index of the report. Look for section headers, numbered items, and chapter titles. Include ALL sections with their numbers. Example format:
- "1. Introduction"
- "2. Inspection Details" 
- "3. Impacted Areas"
- "3.1 Hall & Common Bathroom"
- "4. Inspection Checklists"
- "4.1 WC / Bathroom Checklist"
- "4.2 External Wall Checklist"
- "5. Summary Table"
- "6. Recommendations"
- "7. Limitation and Precaution Note"

### Introduction
- Background: What is this report about? (e.g., "This Detailed Diagnostic Report is prepared for the inspection of Flat No. 103...")
- Objective: What is the purpose of the inspection? (e.g., "To identify sources of leakage, dampness, and structural defects...")
- Scope_of_Work: What areas were inspected? List all rooms and components inspected.
- Tools_Used: List all inspection tools mentioned (e.g., "GTC 400 C Professional Thermal Camera, Moisture Meter, Visual Inspection")

### Metadata
Extract ALL fields carefully from the report header/first pages:
- Report_ID: Any reference number or report ID
- Site_Address: Full address of the inspected property
- Type_of_Structure: e.g., "Residential Building", "Commercial Complex"
- Property_Type: e.g., "Flat", "Villa", "Office"
- Floors: Number of floors
- Year_of_Construction, Age_Building_years: Construction year and age
- Inspection_Date: Exact date in DD.MM.YYYY format
- Inspector_Names: Names of all inspectors
- Customer_Name, Customer_Mobile, Customer_Email: Client contact details

### Summary
- Checklists_Flagged: How many checklists had issues (e.g., "2 out of 3 flagged")
- Score_Percentage: Overall inspection score
- Condition_Stats: Breakdown of conditions found. Count how many items were rated Good, Moderate, and Poor across ALL checklists.

### Impacted_Areas
Each entry represents a pair of negative-side and positive-side observations:
- Area: The specific room/location pair (e.g., "Hall, Common Bathroom")
- Negative_Side_Inputs: What damage/issue was observed on the negative side (e.g., "Skirting level dampness observed in Hall")
- Positive_Side_Inputs: What was found on the positive/source side (e.g., "Tile joint gaps and hollowness in Common Bathroom")
- Associated_Images: ONLY list image filenames from pages that discuss THIS specific area. Match page numbers in image names to the page where this area's text appears.

### Checklists
Extract EVERY checklist table from the report. For each:
- Category_Name: The checklist title (e.g., "WC", "External Wall", "Bathroom", "Balcony", "Terrace")
- Score_Percentage: Calculate as: (count of 'Good' + count of 'No') / total_items * 100
- Items: Each row in the checklist table. The Question is the left column, and the Value is whichever rating column has a tick/mark (Good, Moderate, Poor, Yes, No). For checkboxes, identify which box is checked.

IMPORTANT: Look for sub-checklists within categories. "External Wall" often has sub-sections like:
- Structural Condition of RCC Members
- Condition of Exterior Wall  
- Adhesion of Old Paint
- Substrate Condition of Plaster

### Final_Summary_Table
Each row describes an impacted area with:
- Impacted_Area: Full description with flat number (e.g., "Hall of Flat No. 103, Common Bathroom of Flat No. 103")
- Observed_Issue: Detailed description of what was found
- Probable_Cause: Technical analysis of why the issue occurred
- Severity: MUST be one of "High", "Medium", or "Low":
  * "High" = active leakage, water dripping from ceiling, parking area seepage, structural cracks with water ingress
  * "Medium" = dampness at skirting, efflorescence, tile joint gaps, wall cracks
  * "Low" = mild discoloration, cosmetic issues, minor surface dampness
- Suggested_Remedy: Specific professional remedies such as:
  * "Epoxy injection grouting of tile joints"
  * "Polyurethane sealant for external wall crack repair"
  * "Pressure grouting with cementitious compound"
  * "Waterproofing membrane re-application"
  * "Concealed plumbing leak detection and repair"

### Overall_Recommendations
Provide 4-6 actionable, professional recommendations. Be specific (not generic). Reference the actual findings.

### Limitation_and_Precaution
Extract the full text of Section 5 (Limitation and Precaution Note) if present.

=== CRITICAL RULES ===
1. Do NOT invent information. Use "Not Available" only for genuinely missing data.
2. Image mapping: Match images to areas by PAGE NUMBER. If Area X is described on pages 3-4, only assign images from pages 3-4.
3. Be thorough: Extract ALL checklist items, ALL impacted areas, ALL summary rows.
4. Maintain professional language in remedies and causes.
"""


    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, combined_text],
            config={
                'response_mime_type': 'application/json',
                'response_schema': DDRReport,
            },
        )
        
        parsed_data = json.loads(response.text)
        # Post-process: separate Normal vs Thermal images in code
        parsed_data = _separate_images(parsed_data)
        return parsed_data
    except Exception as e:
        print(f"Failed to generate or parse response from Gemini: {e}")
        raise e

import os
import sys
from dotenv import load_dotenv
from pdf_processor import extract_pdf_content
from llm_analyzer import analyze_with_gemini
from report_generator import generate_pdf
import json

def main():
    load_dotenv(override=True)
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your-key" or os.environ.get("GEMINI_API_KEY") == "put_your_real_api_key_here":
        print("Please set your GEMINI_API_KEY correctly in the .env file.")
        sys.exit(1)
        
    print("1. Extracting text and images from PDFs...")
    sample_data = extract_pdf_content("Sample Report.pdf", "extracted_images", "sample")
    thermal_data = extract_pdf_content("Thermal Images.pdf", "extracted_images", "thermal")
    
    print("2. Sending extracted data to Gemini 2.5 Flash for structural analysis...")
    report_data = analyze_with_gemini(sample_data, thermal_data)
    
    if report_data:
        print("   Analysis successful. Saving data and generating final DDR PDF...")
        # Save JSON output
        json_filename = "Main_DDR_Output.json"
        with open(json_filename, "w") as f:
            json.dump(report_data, f, indent=4)
        print(f"   JSON data saved to '{json_filename}'.")
        
        generate_pdf(report_data, "Main_DDR_Output.pdf", "extracted_images")
        print("   Done! Check 'Main_DDR_Output.pdf'.")
    else:
        print("   Failed to get valid JSON from Gemini.")

if __name__ == "__main__":
    main()

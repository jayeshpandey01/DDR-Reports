# Task

## Applied AI Builder (DDR Report Generation)

## Objective

This task evaluates your ability to design an AI workflow that converts technical inspection
data into a structured, client‑ready report.

You will be given raw site inspection documents. Your goal is to generate a final structured
report similar in clarity and format to a professional deliverable.

This tests reasoning, structuring, reliability, and handling imperfect data.

You may use any tools, models, frameworks, or languages.

## Input Documents Provided

You will receive:

- **Inspection Report (Sample Report.pdf)** - contains site observations and issue
    descriptions
- **Thermal Report (Thermal Images Document.pdf)** - contains temperature readings and
    thermal findings

## Task

Build an AI system that reads both documents and generates a **Main DDR (Detailed
Diagnostic Report.pdf)**.

The system must:

- Extract relevant observations
- Combine information logically


- Avoid duplicate points
- Handle missing or conflicting details
- Present a clear client‑friendly report

### Output Requirements (DDR Structure)

Your generated report must contain:

1. Property Issue Summary
2. Area‑wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information (explicitly mention “Not Available” if needed)

**Additional Requirement**

The AI system must extract **both textual observations and relevant images** from the
provided documents (Inspection Report and Thermal Report). The final DDR should include
these **images placed in the appropriate sections of the report** (for example, under the
corresponding area-wise observation). The report should maintain a **well-structured
format** , ensuring that images support the related findings and improve clarity for the client.

**Important Guidelines for Images**

- Extract images directly from the source documents where relevant.
- Place each image under the **appropriate observation or section** in the DDR.
- Do **not include unrelated images**.
- If an expected image is missing, mention **“Image Not Available.”**

### Important Rules

- Do NOT invent facts not present in the documents


- If information conflicts → mention the conflict
- If information is missing → write “Not Available”
- Use simple, client‑friendly language
- Avoid unnecessary technical jargon
- Your solution should work on similar reports, not only these files

### Evaluation Criteria

We evaluate:

- Accuracy of extracted information
- Logical merging of inspection + thermal data
- Handling of missing/conflicting details
- Clarity of final DDR output
- System thinking and reliability (not UI design)

### Note

The provided documents are sample reports. Your solution should generalise to similar
inspection data.



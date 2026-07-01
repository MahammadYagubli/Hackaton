
import os
import re
import pandas as pd
import gradio as gr
from openai import OpenAI

# =====================================
# CONFIGURATION
# =====================================

EXCEL_FILE = "measures.xlsx"

# Replace with your NEW API key
client = OpenAI(
   api_key=" "
)

# =====================================
# AI FUNCTION
# =====================================

def ask_ai(prompt):

    full_prompt = f"""
{prompt}

Please answer with:

1. Assessment
2. Explanation

Finish EXACTLY with:

Score: XX/100

where XX is an integer.
"""

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=full_prompt
        )

        return response.output_text

    except Exception as e:

        return f"""
API Error

{e}

Score: 0/100
"""


# =====================================
# LOAD EXCEL
# =====================================

def load_measures():

    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(f"{EXCEL_FILE} not found.")

    df = pd.read_excel(EXCEL_FILE)

    required = [
        "Measure Name",
        "Prompt Template",
        "Weight"
    ]

    for col in required:
        if col not in df.columns:
            raise Exception(f"Missing column: {col}")

    return df


# =====================================
# EXTRACT SCORE
# =====================================

def extract_score(text):

    patterns = [
        r"Score[: ]+(\d{1,3})",
        r"(\d{1,3})\s*/\s*100"
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            score = int(match.group(1))
            return max(0, min(score, 100))

    return 50


# =====================================
# ANALYSIS
# =====================================

def analyze_company(company):

    df = load_measures()

    results = []

    weighted_score = 0
    total_weight = 0

    for _, row in df.iterrows():

        measure = str(row["Measure Name"])
        template = str(row["Prompt Template"])
        weight = float(row["Weight"])

        prompt = template.format(company=company)

        print(f"Running: {measure}")

        ai_response = ask_ai(prompt)

        score = extract_score(ai_response)

        weighted_score += score * weight
        total_weight += weight

        results.append(
            {
                "Measure": measure,
                "Score": score,
                "Response": ai_response,
            }
        )

    final_score = round(weighted_score / total_weight, 2)

    return results, final_score


# =====================================
# REPORT
# =====================================

def generate_report(company):

    try:

        if company.strip() == "":
            return "Please enter a company name."

        print("Generating report...")

        results, final_score = analyze_company(company)

        report = f"# Credit Risk Report\n\n"

        report += f"## Company\n"
        report += f"**{company}**\n\n"

        report += f"## Final Weighted Score\n"
        report += f"**{final_score}/100**\n\n"

        report += "---\n\n"

        for item in results:

            report += f"### {item['Measure']}\n\n"

            report += f"**Score:** {item['Score']}/100\n\n"

            report += item["Response"]

            report += "\n\n---\n\n"

        return report

    except Exception as e:

        import traceback

        traceback.print_exc()

        return f"ERROR\n\n{e}"


# =====================================
# GRADIO
# =====================================

demo = gr.Interface(
    fn=generate_report,
    inputs=gr.Textbox(
        label="Company Name",
        placeholder="e.g. Apple, WeWork, Tesla"
    ),
    outputs=gr.Markdown(),
    title="🏦 AI Credit Risk Banking Engine",
    description="Enter a company name and generate an AI credit risk report."
)

# IMPORTANT FOR JUPYTER
demo.launch(
    debug=True,
    inline=False,
    share=False
)

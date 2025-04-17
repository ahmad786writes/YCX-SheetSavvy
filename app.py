import os
import ast
from crewai import Agent, Task, Crew, LLM
from spreadsheet_tools import CompanySearchTool, CompanyDetailsSearchTool

# Set Api as an environment variable
os.environ["GROQ_API_KEY"] = "Your API Key"

# Initialize Large Language Model (LLM) of your choice (see all models on our Models page)
llm = LLM(model="groq/llama-3.3-70b-versatile")

# GoogleSheetCompanyTool usage
google_sheet_names_extract_tool = CompanySearchTool()
google_sheet_details_extract_tool = CompanyDetailsSearchTool()


def company_name_crew():
    # Initializing Agent
    spreadsheet_company_name_extractor_agent = Agent(
        role="Company Name Extractor from Spreadsheet",
        goal="Identify the starting prefix from a user's query and return all company names from the spreadsheet that exactly match that prefix.",
        backstory="You're a data analyst specializing in spreadsheet parsing. " \
        "Your job is to analyze user prompts, extract possible name prefixes (e.g., 'Mic' for Microsoft),"
        " and fetch all matching company names from a live spreadsheet. You do not interpret, guess, or generate—your job is to fetch what exists.",
        verbose=False,
        allow_delegation=False,
        tools=[google_sheet_names_extract_tool],
        llm=llm
    )

    # Tasking Agents
    name_task = Task(
        description=(
            "Given the user prompt: '{prompt}', extract the prefix that represents the beginning of a company name "
            "(e.g., 'Mic' for Microsoft, 'Alp' for Alphabet). Use your tool to fetch all company names from the spreadsheet "
            "that start exactly with the extracted prefix. "
            "Do not guess or add company names yourself — only return what the tool provides. "
            "Return the result strictly as a JSON list of matching company names, without any extra formatting or summaries."
        ),
        agent=spreadsheet_company_name_extractor_agent,
        expected_output = """A JSON list of company names e.g., {"Companies": ["Microsoft", "Micron", "Microchip Technology"]} 
                        that start with the extracted prefix from the user prompt."""
    )
    crew = Crew(agents=[spreadsheet_company_name_extractor_agent], tasks=[name_task], verbose=False)
    return crew

def company_details_crew():
    # Initializing Agent
    spreadsheet_details_extractor_agent = Agent(
        role="Company Detail Retriever from Spreadsheet",
        goal="Take a company name as input from a user and return its complete details from the spreadsheet, only if it matches exactly.",
        backstory="You're a focused data analyst who specializes in pulling detailed, structured information about " \
        "companies from spreadsheets."
        " and you provide the full, raw dataset for that exact company—no assumptions, no extra processing.",
        verbose=False,
        allow_delegation=False,
        tools=[google_sheet_details_extract_tool],
        llm=llm
    )

    details_task = Task(
        description=(
            "You will receive a specific company name selected by the user "
            "Use your tool to search the Google Spreadsheet and return only the full details for the exact company name match. "
            "Ensure the match is exact — not based on prefix, partial name, or fuzzy logic. "
            "Return the company's data as-is, exactly as the tool retrieves it, without adding, modifying, or rephrasing any values. "
            "No summaries, explanations, or assumptions — just raw, unedited data for that exact company."
        ),
        agent=spreadsheet_details_extractor_agent,
        expected_output="A JSON dictionary containing the complete set of details for the selected company name, "
                        "including fields like Company Name, Website URL, Industry, Headquarters, Founding Year, " \
                        "No. of Employees, Funding Raised, Revenue, Valuation, Company Description, Founders & LinkedIn URLs," \
                        "Key Contacts, Social Media Links,AI Model Used, Primary AI Use Case, AI Frameworks Used, AI Products/Services Offered," \
                        " Patent Details, AI Research Papers Published, Partnerships, Technology Stack, Customer Base, Case Studies, " \
                        "Awards and Recognition, Compliance and Regulatory Adherence, Market Presence, Community Engagement, AI Ethics Policies," \
                        "Competitor Analysis, Media Mentions, as provided in the spreadsheet. "
                        "Only return the dictionary for the exact match — no list, no commentary."
    )

    crew = Crew(agents=[spreadsheet_details_extractor_agent], tasks=[details_task], verbose=True)
    return crew


# === PHASE 1 === Name Extraction
print("🔍 Searching for company names...")

names_crew = company_name_crew()

inputs = {"prompt": "get data on companies that start with A"}  # You can change this
company_names = names_crew.kickoff(inputs)

try:
    if not company_names:
        print("🚫 No companies found matching that prefix. Try a different one.")
        exit()
except Exception as e:
    print(f"❌ Failed to parse response or no results: {e}")
    exit()

# === PHASE 2 === Ask User for Company Selection
print(f"\n✅ Found matching companies: {company_names}")
selected_company = input("👉 Please type exactly which company you want details for: ")

# === PHASE 3 === Fetch Details
company_details_crew = company_details_crew()
inputs = {"company_name": selected_company}
print("\n📦 Fetching details...")
details_crew = company_details_crew.kickoff(inputs)

print("\n📊 COMPANY DETAILS:")
print(details_crew)
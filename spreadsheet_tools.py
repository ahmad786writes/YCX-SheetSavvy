import gspread
from oauth2client.service_account import ServiceAccountCredentials
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# ----------------------------------
# Core Function Logic to get Details
# ----------------------------------
def get_company_details_exact_match(company_name):
    company_name = company_name.upper()

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1Gv6u8ucaP87JpsWu-A0nlo-nQw2LABW6P0TldO8VXkk/edit#gid=0"
    ).worksheet("Company Details")

    data = sheet.get_all_records(expected_headers=["Company Name"])

    # Return the first exact match (if any), otherwise None
    filtered = next(
        (
            {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
            for row in data
            if isinstance(row.get("Company Name"), str) and row["Company Name"].strip().upper() == company_name
        ),
        None  # Return None if no match is found
    )

    return filtered

# ---------------------------------------
# Core Function Logic to get company name
# ---------------------------------------
def get_companies_name_starting_with(prefix):
    prefix = prefix.upper()

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1Gv6u8ucaP87JpsWu-A0nlo-nQw2LABW6P0TldO8VXkk/edit#gid=0"
    ).worksheet("Company Details")

    data = sheet.get_all_records(expected_headers=["Company Name"])

    # Return only company names that match the prefix
    company_names = [
        row["Company Name"].strip()
        for row in data
        if isinstance(row.get("Company Name"), str) and row["Company Name"].upper().startswith(prefix)
    ]

    return company_names


# -----------------------
# Input Schema Definition
# -----------------------
class CompanySearchToolInput(BaseModel):
    prefix: str = Field(..., description="The prefix string to match company names with.")
class CompanyDetailsSearchToolInput(BaseModel):
    company: str = Field(..., description="The company names of which the details to return.")

# -----------------------
# CrewAI Tool Class
# -----------------------
class CompanySearchTool(BaseTool):
    name: str = "Company Name Prefix Search"
    description: str = (
        "Searches a Google Sheet for company names starting with the given prefix. "
        "It progressively reduces the prefix until matches are found or all options are exhausted."
    )
    args_schema: Type[BaseModel] = CompanySearchToolInput

    def _run(self, prefix: str) -> str:
        companies = get_companies_name_starting_with(prefix)
        if not companies:
            return "No matching Companies Found...."
        else:
            return companies
        
class CompanyDetailsSearchTool(BaseTool):
    name: str = "Company Details Extractor"
    description:str = (
        "Searches a Google Sheet for an exact company name match. "
        "Returns complete details for the matched company."
    )
    args_schema: Type[BaseModel] = CompanyDetailsSearchToolInput

    def _run(self, company: str) -> str:
        company_details = get_company_details_exact_match(company)
        return company_details
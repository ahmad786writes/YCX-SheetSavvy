import gspread
from oauth2client.service_account import ServiceAccountCredentials
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# -----------------------
# Core Function Logic
# -----------------------
def get_companies_starting_with(prefix):
    prefix = prefix.upper()

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1Gv6u8ucaP87JpsWu-A0nlo-nQw2LABW6P0TldO8VXkk/edit#gid=0"
    ).worksheet("Company List")

    data = sheet.get_all_records(expected_headers=["Company Name "])

    # Return only exact matches with the prefix (no fallback logic)
    filtered = [
        {
            "Company Name": row["Company Name "].strip(),
            "Website URL": row.get("Website URL ", "").strip(),
            "Industry": row.get("Industry ", "").strip(),
            "Valuation": row.get("Valuation", "").strip(),
            "Funding Raised($)": row.get("Funding Raised($)", "").strip(),
            "Headquarters": row.get("Headquarters ", "").strip()
        }
        for row in data
        if isinstance(row["Company Name "], str) and row["Company Name "].upper().startswith(prefix)
    ]

    return filtered

# -----------------------
# Input Schema Definition
# -----------------------
class CompanySearchToolInput(BaseModel):
    prefix: str = Field(..., description="The prefix string to match company names with.")

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
        companies = get_companies_starting_with(prefix)
        if not companies:
            return "No matching Companies Found...."
        else:
            return companies
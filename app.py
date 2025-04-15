import os
from crewai import Agent, Task, Crew, LLM
from spreadsheet_tools import CompanySearchTool


# Set Api as an environment variable
os.environ["GROQ_API_KEY"] = "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"

# Initialize Large Language Model (LLM) of your choice (see all models on our Models page)
llm = LLM(model="groq/llama-3.3-70b-versatile")

# GoogleSheetCompanyTool usage
google_sheet_tool = CompanySearchTool()

# Initializing Agent
spreadsheet_agent = Agent(
    role="Spreadsheet Analyst",
    goal="Fetch and filter company data from a Google Spreadsheet based on User Prompt",
    backstory="You’re a data pro, helping users query spreadsheet records fast and accurately.",
    verbose=True,
    allow_delegation=False,
    tools=[google_sheet_tool],
    llm=llm  # using Groq-powered LLM here
)

# Tasking Agent
task = Task(
    description=(
        "Given the user prompt: '{prompt}', extract the prefix that refers to the starting letters of a company name "
        "(for example, 'Mic' for Microsoft, 'Dec' for Decathlon). Then use your tool to search for companies starting with that prefix. "
        "Return only companies whose names begin with the prefix exactly as retrieved from the tool. "
        "Do not modify, reduce, or make assumptions about the tool’s output. Return the data as is, in its raw JSON format."
    ),
    agent=spreadsheet_agent,
    expected_output="A JSON list of dictionaries containing full company details"
    " (Company Name, Website URL, Industry, Valuation, Funding Raised($), Headquarters)" \
    " for all companies matching the extracted prefix."
)

# crew
crew = Crew(
    agents=[spreadsheet_agent],
    tasks=[task],
    verbose=True
)

# inputs

inputs = {"prompt": "get data on companies that start with Dec"}
result = crew.kickoff(inputs)
print("OUTPUT:")
print(result)
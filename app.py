# app.py
# Standalone FastAPI application to research a company using the Gemini API.
#
# To run this application:
# 1. Install the required libraries:
#    pip install "fastapi[all]" python-dotenv httpx
#
# 2. Get a Google AI API Key:
#    - Go to https://aistudio.google.com/app/apikey
#    - Create a new API key in a new or existing project.
#
# 3. Create a .env file in the same directory as this script
#    and add your API key like this:
#    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
#
# 4. Run the FastAPI server from your terminal:
#    uvicorn app:app --reload
#
# 5. Open your browser and go to http://127.0.0.1:8000/docs
#    to see the interactive API documentation and test the endpoint.

import os

import httpx
from dotenv import load_dotenv
from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

# Load environment variables from a .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Company Research API",
    description="An API that takes a company name and returns a research summary based on web search results, powered by Gemini.",
    version="1.0.0",
)


# --- Pydantic Models ---
class CompanyResearchRequest(BaseModel):
    """Request model for the company research endpoint."""

    company_name: str = Body(
        ..., embed=True, description="The name of the company to research."
    )


class CompanyResearchResponse(BaseModel):
    """Response model for the company research endpoint."""

    report: str


# --- Gemini API Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not found in .env file. Please follow the setup instructions."
    )


# --- API Endpoint ---
@app.post(
    "/research",
    response_model=CompanyResearchResponse,
    tags=["Company Research"],
    summary="Research a company",
    description="Takes a company name and uses the Gemini 1.5 Flash model to conduct a web search and generate a detailed research report.",
)
async def research_company(request_body: CompanyResearchRequest):
    """
    Asynchronously researches a company by calling the Gemini API.

    This endpoint constructs a detailed prompt asking the Gemini model to act as a
    business analyst, perform a web search, and compile a report on the specified
    company.

    Args:
        request_body: A Pydantic model containing the company_name.

    Returns:
        A Pydantic model containing the generated research report.

    Raises:
        HTTPException: If the API call to Gemini fails or returns an error.
    """
    company_name = request_body.company_name

    prompt = f"""
    Please act as a business research analyst.
    Your task is to conduct a thorough web search and compile a detailed report on the following company: "{company_name}".

    Please include the following information in your report:
    1.  **Company Overview:** What they do, their mission, and their primary products or services.
    2.  **History:** When they were founded and key historical milestones.
    3.  **Leadership:** Key executives (CEO, etc.).
    4.  **Financials:** Mention any publicly available information about their revenue, funding rounds, or stock performance if applicable.
    5.  **Recent News:** Summarize any significant news or events from the last 12 months.
    6.  **Market Position:** Briefly describe their main competitors and their position in the market.

    Please ensure the information is accurate and based on reliable web sources. Structure the output in clear, well-organized sections.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(GEMINI_API_URL, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            data = response.json()

            # Navigate the Gemini API response structure to get the text
            if (
                (candidates := data.get("candidates"))
                and (content := candidates[0].get("content"))
                and (parts := content.get("parts"))
            ):
                report_text = parts[0].get("text", "No content generated.")
                return CompanyResearchResponse(report=report_text)
            else:
                # Handle cases where the response structure is unexpected
                error_detail = f"Unexpected API response structure: {data}"
                raise HTTPException(status_code=500, detail=error_detail)

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from the Gemini API
        error_detail = f"Gemini API request failed with status {e.response.status_code}: {e.response.text}"
        raise HTTPException(status_code=502, detail=error_detail)
    except Exception as e:
        # Handle other exceptions like network errors or timeouts
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


# --- Root Endpoint for Health Check ---
@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "API is running"}


# To run this app, use the command: uvicorn app:app --reload

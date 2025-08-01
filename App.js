import React, { useState, useCallback } from 'react';
import { Search, Loader2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// This is the main component for our company research application.
// It handles user input, API calls, and displaying the results.
export default function App() {
  // State variables to manage the application's UI and data.
  const [companyName, setCompanyName] = useState('');
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // The base URL of the FastAPI backend. Update this if your server is elsewhere.
  const API_URL = 'http://127.0.0.1:8000/research';

  /**
   * Fetches a research report for the given company from the FastAPI backend.
   * This function is memoized with useCallback to prevent unnecessary re-creations.
   */
  const handleSearch = useCallback(async (e) => {
    e.preventDefault();
    // Do not proceed if the company name is empty or we're already loading.
    if (!companyName.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setReport(null);

    try {
      // Make a POST request to the FastAPI endpoint.
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // The body must match the Pydantic model in the backend (CompanyResearchRequest).
        body: JSON.stringify({ company_name: companyName }),
      });

      // Check for a successful response. If not, throw an error with the details.
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong with the API call.');
      }

      // Parse the JSON response.
      const data = await response.json();
      // Set the report state with the text from the API response.
      setReport(data.report);

    } catch (err) {
      // Catch and display any errors that occur during the fetch operation.
      console.error('Fetch error:', err);
      setError(err.message || 'Failed to fetch the report. Please try again.');
    } finally {
      // This block runs regardless of success or failure.
      // We set isLoading back to false to enable the form again.
      setIsLoading(false);
    }
  }, [companyName, isLoading]); // Dependencies for useCallback.

  return (
    <div className="min-h-screen bg-slate-900 text-gray-100 p-4 font-sans flex items-center justify-center">
      <div className="w-full max-w-4xl p-8 bg-slate-800 rounded-2xl shadow-xl space-y-8">
        {/* Header Section */}
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white leading-tight mb-2">
            Company Research App
          </h1>
          <p className="text-gray-400 text-lg">
            Powered by a FastAPI backend and the Gemini API.
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter a company name (e.g., Google, Tesla, SpaceX)"
            disabled={isLoading}
            className="flex-grow p-3 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sky-500 transition duration-200"
          />
          <button
            type="submit"
            disabled={isLoading || !companyName.trim()}
            className="relative flex items-center justify-center gap-2 px-6 py-3 bg-sky-600 text-white font-bold rounded-xl shadow-lg hover:bg-sky-700 disabled:bg-sky-800 disabled:cursor-not-allowed transition duration-200"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Search size={20} />
            )}
            {isLoading ? 'Researching...' : 'Research Company'}
          </button>
        </form>

        {/* Status and Results Display Section */}
        <div className="bg-slate-700 p-6 rounded-2xl shadow-inner min-h-[300px]">
          {error && (
            // Error Message
            <div className="flex items-center gap-2 p-4 bg-red-800/50 text-red-300 rounded-xl">
              <AlertCircle size={24} />
              <p className="font-medium">{error}</p>
            </div>
          )}

          {isLoading && !error && (
            // Loading Spinner
            <div className="flex flex-col items-center justify-center h-full text-sky-400 space-y-4">
              <Loader2 className="animate-spin" size={48} />
              <p className="text-lg">Fetching data and generating report...</p>
            </div>
          )}

          {report && !isLoading && !error && (
            // Research Report
            <div className="prose prose-invert max-w-none text-gray-200">
              <ReactMarkdown>{report}</ReactMarkdown>
            </div>
          )}

          {!report && !isLoading && !error && (
            // Initial message
            <div className="flex items-center justify-center h-full text-gray-500">
              <p className="text-xl">
                Enter a company name and click 'Research Company' to get started.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

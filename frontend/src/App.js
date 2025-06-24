import React, { useState } from 'react';
import { Copy, Trash2 } from 'lucide-react'; // Importing icons for copy and delete

const App = () => {
  // State variables for managing the UI and data
  const [originalUrl, setOriginalUrl] = useState(''); // Stores the long URL entered by the user
  const [shortenedUrl, setShortenedUrl] = useState(''); // Stores the short URL received from the backend
  const [message, setMessage] = useState(''); // Stores success or error messages to display to the user
  const [isProcessing, setIsProcessing] = useState(false); // Indicates if an API call is in progress

  // Base URL for your Flask backend API
  // IMPORTANT: Ensure this matches the host and port where your Flask app is running.
  // For local development, it's typically http://127.0.0.1:5000 or http://localhost:5000.
  const API_BASE_URL = 'http://127.0.0.1:5000';

  /**
   * Handles the "Shorten URL" button click.
   * Sends a POST request to the backend to shorten the URL.
   */
  const handleShortenUrl = async () => {
    // Clear previous messages and shortened URL
    setMessage('');
    setShortenedUrl('');
    setIsProcessing(true); // Set processing state to true to show loading indicator

    // Basic client-side validation
    if (!originalUrl.trim()) {
      setMessage('Please enter a URL to shorten.');
      setIsProcessing(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/shorturl`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: originalUrl }), // Send the original URL in the request body
      });

      const data = await response.json(); // Parse the JSON response from the backend

      if (response.ok) {
        // If the request was successful (status 2xx)
        setShortenedUrl(data.short_url); // Update the state with the received short URL
        setMessage('URL shortened successfully!');
        setOriginalUrl(''); // Clear the input field
      } else {
        // If the request failed (status 4xx or 5xx)
        setMessage(`Error: ${data.message || 'Something went wrong.'}`);
      }
    } catch (error) {
      // Handle network errors (e.g., API not reachable)
      setMessage(`Network error: ${error.message}. Please ensure the backend is running.`);
    } finally {
      setIsProcessing(false); // Reset processing state
    }
  };

  /**
   * Handles copying the shortened URL to the clipboard.
   * Uses `document.execCommand('copy')` for compatibility in iframe environments.
   */
  const handleCopyUrl = () => {
    if (shortenedUrl) {
      // Create a temporary textarea element to hold the URL
      const el = document.createElement('textarea');
      el.value = shortenedUrl;
      document.body.appendChild(el); // Append it to the DOM
      el.select(); // Select the text
      document.execCommand('copy'); // Execute the copy command
      document.body.removeChild(el); // Remove the temporary element
      setMessage('Short URL copied to clipboard!');
    }
  };

  /**
   * Handles deleting the currently displayed short URL.
   * Extracts the key from the short URL and sends a DELETE request to the backend.
   */
  const handleDeleteUrl = async () => {
    setMessage('');
    setIsProcessing(true);

    if (!shortenedUrl) {
      setMessage('No short URL to delete.');
      setIsProcessing(false);
      return;
    }

    // Extract the short key from the full short URL (e.g., "http://localhost:5000/key" -> "key")
    const key = shortenedUrl.split('/').pop();

    try {
      const response = await fetch(`${API_BASE_URL}/shorturl/${key}`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Successfully deleted short URL for key: ${key}`);
        setShortenedUrl(''); // Clear the displayed short URL
        setOriginalUrl(''); // Clear original URL input as well
      } else {
        setMessage(`Error deleting URL: ${data.message || 'Something went wrong.'}`);
      }
    } catch (error) {
      setMessage(`Network error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4 font-inter antialiased">
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md transform transition duration-500 hover:scale-105">
        <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-8">
          🔗 shortURL
        </h1>

        <div className="mb-6">
          <label htmlFor="originalUrl" className="block text-gray-700 text-sm font-semibold mb-2">
            Enter Long URL:
          </label>
          <input
            type="url"
            id="originalUrl"
            className="shadow-inner appearance-none border border-gray-300 rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition duration-300 ease-in-out"
            placeholder="e.g., https://www.example.com/very/long/path/to/resource"
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            disabled={isProcessing}
          />
        </div>

        <button
          onClick={handleShortenUrl}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-300 focus:shadow-outline transition duration-300 transform hover:scale-102 active:scale-98 shadow-lg"
          disabled={isProcessing || !originalUrl.trim()} // Disable if processing or input is empty
        >
          {isProcessing ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Shortening...
            </span>
          ) : (
            'Shorten URL'
          )}
        </button>

        {shortenedUrl && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex flex-col sm:flex-row items-center justify-between shadow-md animate-fade-in-up">
            <span className="text-blue-800 break-all text-sm font-medium mb-3 sm:mb-0 sm:mr-4 flex-grow">
              Your Short URL: <a href={shortenedUrl} target="_blank" rel="noopener noreferrer" className="hover:underline text-blue-600 font-bold">
                {shortenedUrl}
              </a>
            </span>
            <div className="flex space-x-2">
              <button
                onClick={handleCopyUrl}
                className="p-3 bg-blue-200 hover:bg-blue-300 text-blue-800 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400 transition duration-300 transform hover:scale-110 active:scale-95"
                title="Copy to clipboard"
              >
                <Copy size={20} />
              </button>
              <button
                onClick={handleDeleteUrl}
                className="p-3 bg-red-200 hover:bg-red-300 text-red-800 rounded-full focus:outline-none focus:ring-2 focus:ring-red-400 transition duration-300 transform hover:scale-110 active:scale-95"
                title="Delete short URL"
              >
                <Trash2 size={20} />
              </button>
            </div>
          </div>
        )}

        {message && (
          <p className={`mt-4 text-center text-sm font-medium p-2 rounded-md ${message.startsWith('Error') || message.startsWith('Network error') ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-green-100 text-green-700 border border-green-200'}`}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default App;

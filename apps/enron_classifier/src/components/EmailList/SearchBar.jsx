import React from 'react';
import { Search, RefreshCcw } from 'lucide-react';

const SearchBar = ({ darkMode, searchQuery, setSearchQuery, refreshEmails }) => {
  return (
    <div
      className={`p-4 ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} border-b flex items-center justify-between`}
    >
      <div className="relative flex-1">
        <input
          type="text"
          placeholder="Search emails..."
          className={`w-full pl-10 pr-4 py-2 ${
            darkMode
              ? 'bg-gray-700 border-gray-600 text-gray-200 focus:ring-blue-400 placeholder-gray-400'
              : 'bg-white border-gray-300 focus:ring-blue-500'
          } border rounded-lg focus:outline-none focus:ring-2 transition-all duration-300`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
      </div>
      <button
        className={`ml-2 p-2 ${
          darkMode
            ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700'
            : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'
        } rounded-full transition-all duration-300 transform hover:rotate-180`}
        onClick={refreshEmails}
      >
        <RefreshCcw size={18} />
      </button>
    </div>
  );
};

export default SearchBar;

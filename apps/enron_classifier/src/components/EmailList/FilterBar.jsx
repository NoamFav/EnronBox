import React from 'react';
import { Filter } from 'lucide-react';

const FilterBar = ({ darkMode, filterOptions, toggleFilterOption, setSort }) => {
  return (
    <div
      className={`px-4 py-2 ${
        darkMode ? 'bg-gray-700 border-gray-700' : 'bg-gray-50 border-gray-200'
      } border-b flex items-center text-sm transition-colors duration-300`}
    >
      <div className="flex items-center">
        <Filter size={14} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
        <span className={`mr-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Filter:</span>
      </div>
      <button
        className={`mr-3 px-2 py-0.5 rounded transition-all duration-300 ${
          filterOptions.unreadOnly
            ? darkMode
              ? 'bg-blue-800 text-blue-200'
              : 'bg-blue-100 text-blue-600'
            : darkMode
              ? 'text-gray-300'
              : 'text-gray-600'
        }`}
        onClick={() => toggleFilterOption('unreadOnly')}
      >
        Unread
      </button>
      <button
        className={`mr-3 px-2 py-0.5 rounded transition-all duration-300 ${
          filterOptions.hasAttachments
            ? darkMode
              ? 'bg-blue-800 text-blue-200'
              : 'bg-blue-100 text-blue-600'
            : darkMode
              ? 'text-gray-300'
              : 'text-gray-600'
        }`}
        onClick={() => toggleFilterOption('hasAttachments')}
      >
        Attachments
      </button>
      <div className="ml-auto flex items-center">
        <span className={darkMode ? 'text-gray-300 mr-1' : 'text-gray-600 mr-1'}>Sort:</span>
        <select
          className={`${
            darkMode
              ? 'bg-transparent border-none text-gray-300'
              : 'bg-transparent border-none text-gray-600'
          } focus:outline-none text-sm transition-colors duration-300`}
          value={filterOptions.sortBy}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="date">Date</option>
          <option value="sender">Sender</option>
          <option value="subject">Subject</option>
        </select>
      </div>
    </div>
  );
};

export default FilterBar;

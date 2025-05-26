import React from 'react';
import { RefreshCcw } from 'lucide-react';

const EmailListStatusBar = ({ darkMode, emails, unreadCount, refreshEmails }) => {
  return (
    <div
      className={`px-4 py-2 ${
        darkMode
          ? 'bg-gray-700 border-gray-700 text-gray-300'
          : 'bg-gray-50 border-gray-200 text-gray-500'
      } border-t text-xs flex items-center transition-colors duration-300`}
    >
      <span>
        {emails.length} email{emails.length !== 1 ? 's' : ''}
      </span>
      <span className="mx-2">•</span>
      <span>{unreadCount} unread</span>
      <button
        className={`ml-auto flex items-center ${
          darkMode ? 'text-gray-400 hover:text-blue-400' : 'text-gray-500 hover:text-blue-500'
        } transition-colors duration-300`}
        onClick={refreshEmails}
      >
        <RefreshCcw size={12} className="mr-1 transform transition-transform hover:rotate-180" />
        <span>Refresh</span>
      </button>
    </div>
  );
};

export default EmailListStatusBar;

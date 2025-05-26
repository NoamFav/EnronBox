import React from 'react';
import { Reply, Forward, Trash, FileText, Printer, MoreHorizontal } from 'lucide-react';

const Actions = ({
  selectedEmail,
  darkMode,
  summarizing,
  replyToEmail,
  forwardEmail,
  deleteEmail,
  summarizeEmail,
  printEmail,
}) => {
  return (
    <div
      className={`p-4 border-t ${darkMode ? 'border-gray-700 bg-gray-700' : 'border-gray-200 bg-gray-50'} flex animate-fadeIn`}
      style={{ animationDelay: '500ms' }}
    >
      <div className="flex space-x-2">
        <button
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center shadow-sm transition-all duration-300 transform hover:scale-105 hover:shadow animate-slideUp group"
          onClick={replyToEmail}
          style={{ animationDelay: '550ms' }}
        >
          <Reply size={16} className="mr-2 transform transition-transform group-hover:rotate-45" />
          Reply
        </button>

        <button
          className={`px-4 py-2 border rounded-lg flex items-center transition-all duration-300 transform hover:scale-105 animate-slideUp group ${
            darkMode
              ? 'border-gray-600 hover:bg-gray-600 text-gray-200'
              : 'border-gray-300 hover:bg-gray-100 text-gray-700'
          }`}
          onClick={forwardEmail}
          style={{ animationDelay: '600ms' }}
        >
          <Forward
            size={16}
            className="mr-2 transform transition-transform group-hover:translate-x-1"
          />
          Forward
        </button>

        <button
          className={`px-4 py-2 border rounded-lg flex items-center transition-all duration-300 transform hover:scale-105 animate-slideUp group ${
            darkMode
              ? 'border-gray-600 hover:bg-gray-600 text-gray-200 hover:text-red-300 hover:border-red-700'
              : 'border-gray-300 hover:bg-red-50 text-gray-700 hover:text-red-600 hover:border-red-200'
          }`}
          onClick={() => deleteEmail(selectedEmail.id, {})}
          style={{ animationDelay: '650ms' }}
        >
          <Trash
            size={16}
            className="mr-2 transform transition-transform group-hover:translate-y-1"
          />
          Delete
        </button>

        <button
          className={`px-4 py-2 border rounded-lg flex items-center transition-colors ${
            darkMode
              ? 'border-gray-600 hover:bg-gray-600 text-gray-200'
              : 'border-gray-300 hover:bg-gray-100 text-gray-700'
          }`}
          onClick={summarizeEmail}
          disabled={summarizing}
        >
          <FileText size={16} className="mr-2" />
          {summarizing ? 'Summarizing...' : 'Summarize'}
        </button>
      </div>

      <div className="ml-auto flex items-center space-x-2">
        <button
          className={`p-2 rounded transition-all duration-300 transform hover:scale-110 animate-fadeIn ${
            darkMode
              ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-600'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
          }`}
          onClick={printEmail}
          title="Print"
          style={{ animationDelay: '700ms' }}
        >
          <Printer size={16} className="transform transition-transform hover:translate-y-0.5" />
        </button>

        <button
          className={`p-2 rounded transition-all duration-300 transform hover:scale-110 animate-fadeIn ${
            darkMode
              ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-600'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
          }`}
          title="More actions"
          style={{ animationDelay: '750ms' }}
        >
          <MoreHorizontal size={16} className="transform transition-transform hover:rotate-90" />
        </button>
      </div>
    </div>
  );
};

export default Actions;

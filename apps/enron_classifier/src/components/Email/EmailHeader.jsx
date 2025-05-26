import React from 'react';
import { AlertCircle, Star, Flag } from 'lucide-react';
import EmailLabels from './EmailLabels';
import SenderAvatar from './SenderAvatar';

const EmailHeader = ({
  selectedEmail,
  darkMode,
  getLabelById,
  lightBadgeClassMap,
  darkBadgeClassMap,
  toggleStarred,
  toggleFlag,
}) => {
  return (
    <div
      className={`p-6 border-b ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} animate-fadeIn transition-colors duration-300`}
    >
      <div className="flex items-center justify-between mb-3">
        <h2 className={`text-xl font-bold ${darkMode ? 'text-gray-100' : ''}`}>
          {selectedEmail.subject}
        </h2>
        <EmailLabels
          labels={selectedEmail.labels}
          getLabelById={getLabelById}
          lightBadgeClassMap={lightBadgeClassMap}
          darkBadgeClassMap={darkBadgeClassMap}
          darkMode={darkMode}
        />
      </div>

      <div className="flex items-center">
        <SenderAvatar sender={selectedEmail.sender} darkMode={darkMode} />

        <div className="ml-3">
          <div className="flex items-center">
            <p className={`font-medium ${darkMode ? 'text-gray-200' : ''}`}>
              {selectedEmail.sender || 'Unknown'}
            </p>
            <span className={`mx-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>•</span>
            <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              {selectedEmail.time}
            </p>
            {selectedEmail.priority === 'high' && (
              <span
                className={`ml-2 px-2 py-0.5 ${darkMode ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800'} text-xs font-medium rounded-full flex items-center animate-pulse`}
              >
                <AlertCircle size={12} className="mr-1" />
                High Priority
              </span>
            )}
          </div>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mt-0.5`}>to me</p>
        </div>

        <div className="ml-auto flex items-center space-x-1">
          <button
            className={`p-1.5 rounded-full transition-all duration-300 ${
              selectedEmail.starred
                ? 'text-yellow-400'
                : darkMode
                  ? 'text-gray-500 hover:text-yellow-400'
                  : 'text-gray-400 hover:text-yellow-400'
            } transform hover:scale-110`}
            onClick={(e) => toggleStarred(selectedEmail.id, e)}
            title={selectedEmail.starred ? 'Unstar' : 'Star'}
          >
            <Star size={18} fill={selectedEmail.starred ? 'currentColor' : 'none'} />
          </button>
          <button
            className={`p-1.5 rounded-full transition-all duration-300 ${
              selectedEmail.flagged
                ? 'text-red-500'
                : darkMode
                  ? 'text-gray-500 hover:text-red-500'
                  : 'text-gray-400 hover:text-red-500'
            } transform hover:scale-110`}
            onClick={(e) => toggleFlag(selectedEmail.id, e)}
            title={selectedEmail.flagged ? 'Remove flag' : 'Flag'}
          >
            <Flag size={18} fill={selectedEmail.flagged ? 'currentColor' : 'none'} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailHeader;

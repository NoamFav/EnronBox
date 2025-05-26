import React from 'react';
import { Mail, Star, Flag, AlertCircle, Paperclip, Archive, Trash, Eye } from 'lucide-react';

const EmailListPanel = ({
  darkMode,
  loading,
  emails,
  selectedEmail,
  handleEmailClick,
  toggleStarred,
  toggleFlag,
  archiveEmail,
  deleteEmail,
  markAsUnread,
  refreshEmails,
  colorClassMap,
  getLabelById,
}) => {
  return (
    <div className="flex-1 overflow-y-auto">
      {loading ? (
        <div className="flex justify-center items-center p-8">
          <div
            className={`animate-spin rounded-full h-8 w-8 border-b-2 ${darkMode ? 'border-blue-400' : 'border-blue-500'}`}
          ></div>
        </div>
      ) : emails.length === 0 ? (
        <div className="flex flex-col justify-center items-center p-8 h-full animate-fadeIn">
          <Mail size={48} className={darkMode ? 'text-gray-600' : 'text-gray-300'} />
          <p className={darkMode ? 'text-gray-400 mt-4' : 'text-gray-500 mt-4'}>
            No emails in this folder
          </p>
          <button
            className={`mt-2 text-sm hover:underline ${darkMode ? 'text-blue-400' : 'text-blue-500'} transition-colors duration-300`}
            onClick={refreshEmails}
          >
            Refresh
          </button>
        </div>
      ) : (
        <div>
          {emails.map((email, index) => (
            <div
              key={email.id}
              className={`px-4 py-3 cursor-pointer transition-all duration-200 relative animate-fadeIn
                ${
                  darkMode
                    ? `border-b border-gray-700 hover:bg-gray-700 ${!email.read ? 'bg-blue-900 bg-opacity-20' : ''} ${selectedEmail?.id === email.id ? 'bg-gray-700' : ''}`
                    : `border-b border-gray-200 hover:bg-gray-50 ${!email.read ? 'bg-blue-50' : ''} ${selectedEmail?.id === email.id ? 'bg-gray-100' : ''}`
                }`}
              onClick={() => handleEmailClick(email)}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {email.priority === 'high' && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-red-500"></div>
              )}
              <div className="flex items-center mb-1.5">
                <div className="flex space-x-2 items-center">
                  <button
                    className={`hover:text-yellow-400 transition-colors duration-300 transform hover:scale-110 ${email.starred ? 'text-yellow-400' : darkMode ? 'text-gray-500' : 'text-gray-400'}`}
                    onClick={(e) => toggleStarred(email.id, e)}
                  >
                    <Star size={16} fill={email.starred ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    className={`hover:text-red-500 transition-colors duration-300 transform hover:scale-110 ${email.flagged ? 'text-red-500' : darkMode ? 'text-gray-500' : 'text-gray-400'}`}
                    onClick={(e) => toggleFlag(email.id, e)}
                  >
                    <Flag size={16} fill={email.flagged ? 'currentColor' : 'none'} />
                  </button>
                </div>
                <span
                  className={`ml-2 font-medium ${darkMode ? 'text-gray-200' : ''} ${!email.read ? 'font-semibold' : ''}`}
                >
                  {email.sender || 'Unknown'}
                </span>
                <span
                  className={`ml-auto text-xs flex items-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
                >
                  {email.time}
                  {email.priority === 'high' && (
                    <AlertCircle size={12} className="ml-1 text-red-500 animate-pulse" />
                  )}
                </span>
              </div>
              <div className="flex items-center">
                <h3
                  className={`text-sm ${darkMode ? 'text-gray-300' : ''} ${!email.read ? 'font-semibold' : ''}`}
                >
                  {email.subject}
                </h3>
              </div>
              <div className="flex items-start mt-1">
                <p
                  className={`text-xs truncate flex-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
                >
                  {email.content}
                </p>
                <div className="flex items-center space-x-1 ml-2">
                  {email.labels.map((labelId) => {
                    const lbl = getLabelById(labelId);
                    if (!lbl) return null;
                    const dotClass = colorClassMap[lbl.name] || 'bg-gray-500';
                    return (
                      <div
                        key={labelId}
                        className={`w-2 h-2 rounded-full ${dotClass}`}
                        title={lbl.name}
                      />
                    );
                  })}
                  {email.hasAttachments && (
                    <Paperclip size={14} className={darkMode ? 'text-gray-500' : 'text-gray-400'} />
                  )}
                </div>
              </div>
              <div
                className={`absolute right-0 top-0 bottom-0 flex items-center justify-end px-2 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity duration-300 ${
                  darkMode
                    ? 'bg-gradient-to-l from-gray-800 via-gray-800 to-transparent'
                    : 'bg-gradient-to-l from-white via-white to-transparent'
                }`}
              >
                <button
                  className={`p-1.5 rounded transform transition-transform hover:scale-110 ${darkMode ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700' : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'}`}
                  onClick={(e) => archiveEmail(email.id, e)}
                  title="Archive"
                >
                  <Archive size={14} />
                </button>
                <button
                  className={`p-1.5 rounded transform transition-transform hover:scale-110 ${darkMode ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700' : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'}`}
                  onClick={(e) => deleteEmail(email.id, e)}
                  title="Delete"
                >
                  <Trash size={14} />
                </button>
                <button
                  className={`p-1.5 rounded transform transition-transform hover:scale-110 ${darkMode ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700' : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'}`}
                  onClick={(e) => markAsUnread(email.id, e)}
                  title="Mark as unread"
                >
                  <Eye size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmailListPanel;

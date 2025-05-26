import React from 'react';
import { File, Download } from 'lucide-react';

const Attachments = ({ attachments, darkMode }) => {
  if (!attachments || attachments.length === 0) return null;

  const getAttachmentIcon = (type) => {
    return (
      <div
        className={`w-8 h-8 rounded flex items-center justify-center mr-3 ${
          type === 'pdf'
            ? darkMode
              ? 'bg-red-900 text-red-300'
              : 'bg-red-100 text-red-500'
            : darkMode
              ? 'bg-blue-900 text-blue-300'
              : 'bg-blue-100 text-blue-500'
        } transform transition-transform group-hover:rotate-3`}
      >
        <File size={16} className="transition-all duration-300 transform group-hover:scale-110" />
      </div>
    );
  };

  return (
    <div
      className={`mt-6 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'} pt-4 animate-fadeIn`}
      style={{ animationDelay: '300ms' }}
    >
      <h3
        className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-3 animate-slideUp`}
        style={{ animationDelay: '350ms' }}
      >
        Attachments ({attachments.length})
      </h3>
      <div className="flex flex-wrap gap-3">
        {attachments.map((attachment, index) => (
          <div
            key={index}
            className={`flex items-center p-3 border rounded-lg ${
              darkMode
                ? 'border-gray-700 bg-gray-700 hover:bg-gray-600'
                : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
            } transition-all duration-300 transform hover:scale-105 hover:shadow-md animate-fadeIn group`}
            style={{ animationDelay: `${400 + index * 100}ms` }}
          >
            {getAttachmentIcon(attachment.type)}
            <div className="transition-all duration-300 transform group-hover:translate-x-1">
              <p className={`text-sm font-medium ${darkMode ? 'text-gray-200' : ''}`}>
                {attachment.name}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                {attachment.size}
              </p>
            </div>
            <button
              className={`ml-4 ${
                darkMode ? 'text-gray-400 hover:text-blue-300' : 'text-gray-500 hover:text-blue-500'
              } transition-all duration-300 transform hover:scale-125`}
              title="Download"
            >
              <Download
                size={14}
                className="transition-all duration-300 transform hover:translate-y-1"
              />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Attachments;

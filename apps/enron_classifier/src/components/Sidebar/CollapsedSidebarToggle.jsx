import React from 'react';
import { Menu, Inbox, Send, Star, Trash } from 'lucide-react';

const CollapsedSidebarToggle = ({ darkMode, setShowSidebar }) => {
  return (
    <div
      className={`w-12 ${
        darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
      } border-r flex flex-col items-center py-4 transition-all duration-300 ease-in-out`}
    >
      <button
        className={`w-8 h-8 mb-4 flex items-center justify-center ${
          darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-blue-500'
        } transform transition-transform hover:scale-110`}
        onClick={() => setShowSidebar(true)}
      >
        <Menu size={20} />
      </button>
      {[Inbox, Send, Star, Trash].map((Icon, index) => (
        <button
          key={index}
          className={`w-8 h-8 mb-3 flex items-center justify-center ${
            darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-blue-500'
          } transform transition-transform hover:scale-110`}
        >
          <Icon size={20} />
        </button>
      ))}
    </div>
  );
};

export default CollapsedSidebarToggle;

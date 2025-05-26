import React from 'react';
import { Inbox, Send, Star, File, Trash, Archive } from 'lucide-react';

const FolderList = ({ folders, activeFolder, handleSelectFolder, unreadCount, darkMode }) => {
  const getFolderIcon = (folder) => {
    const folderLower = folder.toLowerCase();
    switch (folderLower) {
      case 'inbox':
        return <Inbox size={18} className="mr-3" />;
      case 'sent':
        return <Send size={18} className="mr-3" />;
      case 'starred':
        return <Star size={18} className="mr-3" />;
      case 'drafts':
        return <File size={18} className="mr-3" />;
      case 'trash':
        return <Trash size={18} className="mr-3" />;
      case 'archive':
        return <Archive size={18} className="mr-3" />;
      default:
        return <File size={18} className="mr-3" />;
    }
  };

  return (
    <ul>
      {folders.map((folder) => (
        <li
          key={folder}
          className={`flex items-center px-4 py-2 cursor-pointer ${
            darkMode
              ? `hover:bg-gray-700 ${activeFolder === folder ? 'bg-gray-700 text-blue-400' : 'text-gray-300'}`
              : `hover:bg-gray-100 ${activeFolder === folder ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`
          } transition-all duration-150`}
          onClick={() => handleSelectFolder(folder)}
        >
          {getFolderIcon(folder)}
          <span className="text-sm">{folder}</span>
          {folder.toLowerCase() === 'inbox' && unreadCount > 0 && (
            <span className="ml-auto bg-blue-500 text-white text-xs font-medium px-2 py-0.5 rounded-full animate-pulse">
              {unreadCount}
            </span>
          )}
        </li>
      ))}
    </ul>
  );
};

export default FolderList;

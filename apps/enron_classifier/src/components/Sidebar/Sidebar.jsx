import React from 'react';
import { Mail, User, Settings } from 'lucide-react';
import UserSelector from './UserSelector';
import LabelList from './LabelList';
import FolderList from './FolderList';

const Sidebar = ({
  darkMode,
  currentUser,
  handleSelectUser,
  composeNewEmail,
  folders,
  activeFolder,
  showFolders,
  setShowFolders,
  handleSelectFolder,
  unreadCount,
  labels,
  showLabels,
  setShowLabels,
  filterOptions,
  toggleFilterByLabel,
  colorClassMap,
}) => {
  return (
    <>
      <div
        className={`w-64 ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r flex flex-col shadow-sm transition-all duration-300 ease-in-out`}
      >
        {/* Header */}
        <div
          className={`p-4 flex items-center justify-center ${darkMode ? 'border-gray-700' : 'border-gray-200'} border-b`}
        >
          <h1 className={`text-xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
            EnronBox
          </h1>
        </div>

        {/* User Selector */}
        <div className={`px-4 py-3 ${darkMode ? 'bg-gray-700' : 'bg-blue-50'}`}>
          <UserSelector
            onSelectUser={handleSelectUser}
            currentUser={currentUser}
            darkMode={darkMode}
          />
        </div>

        {/* Compose Button */}
        <button
          className={`mx-4 my-3 ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white px-4 py-2 rounded-lg flex items-center justify-center shadow-sm transition-all duration-150 hover:shadow transform hover:scale-105`}
          onClick={composeNewEmail}
        >
          <Mail size={16} className="mr-2" />
          <span>Compose</span>
        </button>

        {/* Navigation */}
        <nav className="mt-2 flex-1 overflow-y-auto">
          {/* Folders */}
          <FolderList
            folders={folders}
            showFolders={showFolders}
            setShowFolders={setShowFolders}
            activeFolder={activeFolder}
            handleSelectFolder={handleSelectFolder}
            unreadCount={unreadCount}
            darkMode={darkMode}
          />

          {/* Labels Section */}
          <LabelList
            labels={labels}
            showLabels={showLabels}
            setShowLabels={setShowLabels}
            filterOptions={filterOptions}
            toggleFilterByLabel={toggleFilterByLabel}
            colorClassMap={colorClassMap}
            darkMode={darkMode}
          />
        </nav>

        {/* User Info Footer */}
        <div
          className={`p-4 ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} border-t`}
        >
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white">
              <User size={16} />
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                {currentUser?.username || 'No User'}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                {currentUser ? `${currentUser.username}@enron.com` : ''}
              </p>
            </div>
            <button
              className={`ml-auto ${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'} transform transition-transform hover:rotate-45`}
            >
              <Settings size={16} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;

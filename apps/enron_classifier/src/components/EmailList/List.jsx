import React from 'react';
import SearchBar from './SearchBar';
import FilterBar from './FilterBar';
import Panel from './Panel';
import StatusBar from './StatusBar';

const List = ({
  darkMode,
  searchQuery,
  setSearchQuery,
  refreshEmails,
  filterOptions,
  toggleFilterOption,
  setSort,
  loading,
  emails,
  selectedEmail,
  handleEmailClick,
  toggleStarred,
  toggleFlag,
  archiveEmail,
  deleteEmail,
  markAsUnread,
  getLabelById,
  colorClassMap,
  unreadCount,
}) => {
  return (
    <div
      className={`w-1/3 ${
        darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
      } border-r overflow-hidden flex flex-col transition-colors duration-300`}
    >
      <SearchBar
        darkMode={darkMode}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        refreshEmails={refreshEmails}
      />

      <FilterBar
        darkMode={darkMode}
        filterOptions={filterOptions}
        toggleFilterOption={toggleFilterOption}
        setSort={setSort}
      />

      <Panel
        darkMode={darkMode}
        loading={loading}
        emails={emails}
        selectedEmail={selectedEmail}
        handleEmailClick={handleEmailClick}
        toggleStarred={toggleStarred}
        toggleFlag={toggleFlag}
        archiveEmail={archiveEmail}
        deleteEmail={deleteEmail}
        markAsUnread={markAsUnread}
        refreshEmails={refreshEmails}
        getLabelById={getLabelById}
        colorClassMap={colorClassMap}
      />

      <StatusBar
        darkMode={darkMode}
        emails={emails}
        unreadCount={unreadCount}
        refreshEmails={refreshEmails}
      />
    </div>
  );
};

export default List;

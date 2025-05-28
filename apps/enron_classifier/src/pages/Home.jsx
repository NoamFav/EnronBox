import React, { useEffect } from 'react';
import { EmailProvider, useEmail } from '../contexts/EmailContext';
import { UIProvider, useUI } from '../contexts/UIContext';
import { useEmailActions } from '../hooks/useEmailActions';
import { useEmailAPI } from '../hooks/useEmailAPI';
import { useFilters } from '../hooks/useFilters';
import { useUserActions } from '../hooks/useUserActions';
import { useNotifications } from '../hooks/useNotifications';
import { COLOR_CLASS_MAP, LIGHT_BADGE_CLASS_MAP, DARK_BADGE_CLASS_MAP } from '../utils/constants';

import Sidebar from '../components/Sidebar/Sidebar';
import NotificationPanel from '../components/Notifications/Panel';
import EmailList from '../components/EmailList/List';
import EmailContent from '../components/Email/Content';
import ToastNotification from '../components/Toast';

const HomeContent = () => {
  const { state } = useEmail();
  const {
    darkMode,
    showLabels,
    showFolders,
    setShowLabels,
    setShowFolders,
    showNotifications,
    setShowNotifications,
    showToast,
    setShowToast,
    toastMessage,
    displayToast,
    toggleDarkMode,
  } = useUI();

  const emailActions = useEmailActions();
  const { fetchFolders, fetchEmails, summarizeEmail } = useEmailAPI();
  const filters = useFilters();
  const userActions = useUserActions();
  const notifications = useNotifications();

  // Fetch folders when user changes
  useEffect(() => {
    if (state.currentUser?.username) {
      console.log('User selected, fetching folders:', state.currentUser.username);
      fetchFolders(state.currentUser.username);
      displayToast(`Loaded mailbox for ${state.currentUser.username}`);
    }
  }, [state.currentUser?.username]); // Only depend on username

  // Fetch emails when user or folder changes
  useEffect(() => {
    if (state.currentUser?.username && state.activeFolder) {
      console.log('Fetching emails for:', state.currentUser.username, state.activeFolder);
      fetchEmails(state.currentUser.username, state.activeFolder);
    }
  }, [state.currentUser?.username, state.activeFolder]); // Depend on both username and folder

  // Refetch emails when filter options change
  useEffect(() => {
    if (state.currentUser?.username && state.activeFolder && state.emails.length > 0) {
      console.log('Filter options changed, refetching emails');
      fetchEmails(state.currentUser.username, state.activeFolder);
    }
  }, [
    state.filterOptions.unreadOnly,
    state.filterOptions.hasAttachments,
    state.filterOptions.byLabel,
    state.filterOptions.sortBy,
    state.filterOptions.byStar,
    state.filterOptions.byFlag,
  ]);

  // Helper functions
  const getLabelById = (id) => {
    return state.labels.find((label) => label.id === id) || null;
  };

  const unreadCount = state.emails.filter((email) => !email.read).length;

  return (
    <div
      className={`flex h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-100'} transition-colors duration-300`}
    >
      <ToastNotification
        show={showToast}
        message={toastMessage}
        onClose={() => setShowToast(false)}
      />

      <Sidebar
        darkMode={darkMode}
        currentUser={state.currentUser}
        handleSelectUser={userActions.handleSelectUser}
        composeNewEmail={emailActions.composeNewEmail}
        folders={state.folders}
        activeFolder={state.activeFolder}
        showFolders={showFolders}
        setShowFolders={setShowFolders}
        handleSelectFolder={userActions.handleSelectFolder}
        unreadCount={unreadCount}
        labels={state.labels}
        showLabels={showLabels}
        setShowLabels={setShowLabels}
        filterOptions={state.filterOptions}
        toggleFilterByLabel={filters.toggleFilterByLabel}
        colorClassMap={COLOR_CLASS_MAP}
      />

      <EmailList
        darkMode={darkMode}
        searchQuery={state.searchQuery}
        setSearchQuery={userActions.setSearchQuery}
        refreshEmails={emailActions.refreshEmails}
        filterOptions={state.filterOptions}
        toggleFilterOption={filters.toggleFilterOption}
        setSort={filters.setSort}
        loading={state.loading}
        emails={state.emails}
        selectedEmail={state.selectedEmail}
        handleEmailClick={emailActions.handleEmailClick}
        toggleStarred={emailActions.toggleStarred}
        toggleFlag={emailActions.toggleFlag}
        archiveEmail={emailActions.archiveEmail}
        deleteEmail={emailActions.deleteEmail}
        markAsUnread={emailActions.markAsUnread}
        getLabelById={getLabelById}
        colorClassMap={COLOR_CLASS_MAP}
        unreadCount={unreadCount}
      />

      <EmailContent
        selectedEmail={state.selectedEmail}
        darkMode={darkMode}
        activeFolder={state.activeFolder}
        emailSummary={state.emailSummary}
        summarizing={state.summarizing}
        getLabelById={getLabelById}
        lightBadgeClassMap={LIGHT_BADGE_CLASS_MAP}
        darkBadgeClassMap={DARK_BADGE_CLASS_MAP}
        toggleStarred={emailActions.toggleStarred}
        toggleFlag={emailActions.toggleFlag}
        replyToEmail={emailActions.replyToEmail}
        forwardEmail={emailActions.forwardEmail}
        deleteEmail={emailActions.deleteEmail}
        summarizeEmail={summarizeEmail}
        printEmail={emailActions.printEmail}
      />

      <NotificationPanel
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        unreadNotifications={notifications.unreadNotifications}
        notifications={notifications.notifications}
        markAllNotificationsRead={notifications.markAllNotificationsRead}
      />
    </div>
  );
};

const Home = () => {
  return (
    <UIProvider>
      <EmailProvider>
        <HomeContent />
      </EmailProvider>
    </UIProvider>
  );
};

export default Home;

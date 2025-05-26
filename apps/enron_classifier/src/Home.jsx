import React, { useState, useEffect } from 'react';

import Sidebar from './components/Sidebar/Sidebar';
import NotificationPanel from './components/Notifications/Panel';
import EmailList from './components/EmailList/List';
import EmailContent from './components/Email/Content';
import ToastNotification from './components/Toast';

const Home = () => {
  // Add state for users and folders
  const [currentUser, setCurrentUser] = useState(null);
  const [folders, setFolders] = useState([]);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, text: 'New settings update available', read: false },
    { id: 2, text: 'Storage limit reached 80%', read: false },
    { id: 3, text: '2 new email drafts saved', read: true },
  ]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [showLabels, setShowLabels] = useState(false);
  const [labels, setLabels] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    unreadOnly: false,
    hasAttachments: false,
    sortBy: 'date',
    byLabel: null,
  });
  const [customFolders, setCustomFolders] = useState([
    { id: 1, name: 'Projects', icon: 'Folder' },
    { id: 2, name: 'Newsletters', icon: 'Mail' },
  ]);
  // Add state for summarization
  const [summarizing, setSummarizing] = useState(false);
  const [emailSummary, setEmailSummary] = useState('');
  // Dark mode state
  const [darkMode, setDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode === 'true' || false;
  });
  const colorClassMap = {
    Work: 'bg-blue-500',
    Urgent: 'bg-red-500',
    Business: 'bg-amber-500',
    Personal: 'bg-green-500',
    Meeting: 'bg-teal-500',
    External: 'bg-gray-500',
    Newsletter: 'bg-purple-500',
  };

  const lightBadgeClassMap = {
    Work: 'bg-blue-100 text-blue-800',
    Urgent: 'bg-red-100 text-red-800',
    Business: 'bg-amber-100 text-amber-800',
    Personal: 'bg-green-100 text-green-800',
    Meeting: 'bg-teal-100 text-teal-800',
    External: 'bg-gray-100 text-gray-800',
    Newsletter: 'bg-purple-100 text-purple-800',
  };

  const darkBadgeClassMap = {
    Work: 'bg-blue-900 text-blue-200',
    Urgent: 'bg-red-900 text-red-200',
    Business: 'bg-amber-900 text-amber-200',
    Personal: 'bg-green-900 text-green-200',
    Meeting: 'bg-teal-900 text-teal-200',
    External: 'bg-gray-900 text-gray-200',
    Newsletter: 'bg-purple-900 text-purple-200',
  };
  // Apply dark mode when it changes
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Toggle dark mode function
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    displayToast(darkMode ? 'Light mode enabled' : 'Dark mode enabled');
  };

  // Fetch folders when user changes
  useEffect(() => {
    if (currentUser) {
      fetchFolders(currentUser.username);
      setSelectedEmail(null);
      displayToast(`Loaded mailbox for ${currentUser.username}`);
    }
  }, [currentUser]);

  // Fetch emails when folder changes
  useEffect(() => {
    if (currentUser && activeFolder) {
      fetchEmails(currentUser.username, activeFolder);
    }
  }, [currentUser, activeFolder, filterOptions]);

  const fetchFolders = async (username) => {
    try {
      const response = await fetch(`http://localhost:5050/api/users/${username}/folders`);
      if (response.ok) {
        const data = await response.json();
        setFolders(data);
        // Set active folder to first folder if available
        if (data.length > 0 && !data.includes(activeFolder)) {
          setActiveFolder(data[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
      displayToast('Failed to load folders', 'error');
    }
  };

  const fetchEmails = async (username, folder) => {
    setLoading(true);
    try {
      const resp = await fetch(
        `http://localhost:5050/api/users/${username}/folders/${folder}/emails`
      );
      if (!resp.ok) throw new Error('Email fetch failed');
      const raw = await resp.json();

      const formatted = raw.map((e) => ({
        id: e.id,
        sender: e.from_address,
        subject: e.subject || '(No Subject)',
        content: e.body,
        read: Math.random() > 0.5,
        starred: Math.random() > 0.7,
        time: formatDate(e.date),
        rawTime: e.date,
        hasAttachments: Math.random() > 0.7,
        priority: Math.random() > 0.8 ? 'high' : Math.random() > 0.5 ? 'medium' : 'normal',
        flagged: Math.random() > 0.85,
        attachments:
          Math.random() > 0.7
            ? [
                { name: 'document.pdf', size: '2.4 MB', type: 'pdf' },
                { name: 'image.jpg', size: '1.1 MB', type: 'image' },
              ]
            : [],
        labels: [],
      }));

      const batchRes = await fetch('http://localhost:5050/api/classify/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          formatted.map((e) => ({
            id: e.id,
            subject: e.subject,
            body: e.content,
            sender: e.sender,
            has_attachment: e.hasAttachments,
            num_recipients: 1,
            time_sent: e.rawTime,
          }))
        ),
      });
      if (!batchRes.ok) {
        const err = await batchRes.json().catch(() => ({}));
        console.error('Batch classify error payload:', err);
        throw new Error(`Batch classify failed: ${err.error || batchRes.statusText}`);
      }
      const results = await batchRes.json(); // [{ email_id, classification }, ...]

      const byCategory = new Map(
        results.map((r) => [Number(r.email_id), r.classification.category])
      );

      const allCategories = [
        'Work',
        'Urgent',
        'Business',
        'Personal',
        'Meeting',
        'External',
        'Newsletter',
      ];
      const colorMap = {
        Work: 'blue',
        Urgent: 'red',
        Business: 'orange',
        Personal: 'green',
        Meeting: 'teal',
        External: 'gray',
        Newsletter: 'purple',
      };
      const usedNames = Array.from(
        new Set(Array.from(byCategory.values()).filter((c) => allCategories.includes(c)))
      );
      const derivedLabels = usedNames.map((name, i) => ({
        id: i + 1,
        name,
        color: colorMap[name] || 'gray',
      }));
      setLabels(derivedLabels);

      const nameToId = new Map(derivedLabels.map((l) => [l.name, l.id]));
      const classified = formatted.map((e) => {
        const cat = byCategory.get(e.id);
        const lid = nameToId.get(cat);
        return { ...e, labels: lid ? [lid] : [] };
      });

      let filtered = classified;

      // unread & attachments as before
      if (filterOptions.unreadOnly) filtered = filtered.filter((e) => !e.read);
      if (filterOptions.hasAttachments) filtered = filtered.filter((e) => e.hasAttachments);

      if (filterOptions.byLabel) {
        filtered = filtered.filter((e) => {
          // e.labels is an array of label‐IDs
          return e.labels.some((id) => {
            const lbl = getLabelById(id);
            return lbl?.name === filterOptions.byLabel;
          });
        });
      }

      switch (filterOptions.sortBy) {
        case 'sender':
          filtered.sort((a, b) => a.sender.localeCompare(b.sender));
          break;
        case 'subject':
          filtered.sort((a, b) => a.subject.localeCompare(b.subject));
          break;
      }

      setEmails(filtered);
    } catch (error) {
      console.error('Error fetching or classifying emails:', error);
      displayToast('Failed to load & classify emails', 'error');
    } finally {
      setLoading(false);
    }
  };

  const displayToast = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 3000);
  };

  // Format date for display
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';

    try {
      const date = new Date(dateStr);
      const now = new Date();
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);

      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
    } catch (e) {
      return 'Invalid date';
    }
  };

  const handleEmailClick = (email) => {
    setSelectedEmail(email);
    // Reset summary when selecting a new email
    setEmailSummary('');
    // Mark as read (in a real app, you'd update this in the database)
    setEmails(emails.map((e) => (e.id === email.id ? { ...e, read: true } : e)));
  };

  const toggleStarred = (id, e) => {
    e.stopPropagation();
    setEmails(
      emails.map((email) => {
        if (email.id === id) {
          displayToast(`Email ${!email.starred ? 'starred' : 'unstarred'}`);
          return { ...email, starred: !email.starred };
        }
        return email;
      })
    );
  };

  const toggleFlag = (id, e) => {
    e.stopPropagation();
    setEmails(
      emails.map((email) => {
        if (email.id === id) {
          displayToast(`Email ${!email.flagged ? 'flagged' : 'unflagged'}`);
          return { ...email, flagged: !email.flagged };
        }
        return email;
      })
    );
  };

  const markAsUnread = (id, e) => {
    e.stopPropagation();
    setEmails(
      emails.map((email) => {
        if (email.id === id) {
          displayToast('Email marked as unread');
          return { ...email, read: false };
        }
        return email;
      })
    );
  };

  const deleteEmail = (id, e) => {
    e.stopPropagation();
    setEmails(emails.filter((email) => email.id !== id));
    if (selectedEmail && selectedEmail.id === id) {
      setSelectedEmail(null);
    }
    displayToast('Email moved to trash');
  };

  const archiveEmail = (id, e) => {
    e.stopPropagation();
    setEmails(emails.filter((email) => email.id !== id));
    if (selectedEmail && selectedEmail.id === id) {
      setSelectedEmail(null);
    }
    displayToast('Email archived');
  };

  const handleSelectUser = (user) => {
    setCurrentUser(user);
    setSelectedEmail(null);
  };

  const handleSelectFolder = (folder) => {
    setActiveFolder(folder);
    setSelectedEmail(null);
  };

  const toggleFilterOption = (option) => {
    setFilterOptions({
      ...filterOptions,
      [option]: !filterOptions[option],
    });
  };

  const toggleFilterByLabel = (labelName) => {
    setFilterOptions((opts) => ({
      ...opts,
      // if you click the same label again, clear the filter
      byLabel: opts.byLabel === labelName ? null : labelName,
    }));
  };

  const setSort = (sortOption) => {
    setFilterOptions({
      ...filterOptions,
      sortBy: sortOption,
    });
  };

  // Helper to get label details by id
  const getLabelById = (id) => {
    return labels.find((label) => label.id === id) || null;
  };

  // Count unread emails
  const unreadCount = emails.filter((email) => !email.read).length;

  // Count unread notifications
  const unreadNotifications = notifications.filter((n) => !n.read).length;

  const markAllNotificationsRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
  };

  const replyToEmail = () => {
    displayToast('Reply window opened');
  };

  const forwardEmail = () => {
    displayToast('Forward window opened');
  };

  const printEmail = () => {
    displayToast('Preparing to print');
  };

  const summarizeEmail = async () => {
    if (!selectedEmail || !selectedEmail.content) {
      displayToast('No content to summarize', 'error');
      return;
    }

    setSummarizing(true);
    setEmailSummary('');

    try {
      const response = await fetch('http://localhost:5050/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_text: selectedEmail.content,
          num_sentences: 3,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setEmailSummary(data.summary);
        displayToast('Email summarized successfully');
      } else {
        displayToast('Failed to summarize email', 'error');
        console.error('Summarize API error:', await response.text());
      }
    } catch (error) {
      console.error('Error summarizing email:', error);
      displayToast('Failed to summarize email', 'error');
    } finally {
      setSummarizing(false);
    }
  };

  const refreshEmails = () => {
    fetchEmails(currentUser.username, activeFolder);
    displayToast('Refreshing emails');
  };

  const composeNewEmail = () => {
    displayToast('New email composition window opened');
  };

  return (
    <div
      className={`flex h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-100'} transition-colors duration-300`}
    >
      {/* Toast Notification */}
      <ToastNotification
        show={showToast}
        message={toastMessage}
        onClose={() => setShowToast(false)}
      />{' '}
      {/* Sidebar */}
      <Sidebar
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
        darkMode={darkMode}
        currentUser={currentUser}
        handleSelectUser={handleSelectUser}
        composeNewEmail={composeNewEmail}
        folders={folders}
        activeFolder={activeFolder}
        handleSelectFolder={handleSelectFolder}
        unreadCount={unreadCount}
        labels={labels}
        showLabels={showLabels}
        setShowLabels={setShowLabels}
        filterOptions={filterOptions}
        toggleFilterByLabel={toggleFilterByLabel}
        colorClassMap={colorClassMap}
        customFolders={customFolders}
      />
      {/* Email List */}
      <EmailList
        darkMode={darkMode}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        refreshEmails={refreshEmails}
        filterOptions={filterOptions}
        toggleFilterOption={toggleFilterOption}
        setSort={setSort}
        loading={loading}
        emails={emails}
        selectedEmail={selectedEmail}
        handleEmailClick={handleEmailClick}
        toggleStarred={toggleStarred}
        toggleFlag={toggleFlag}
        archiveEmail={archiveEmail}
        deleteEmail={deleteEmail}
        markAsUnread={markAsUnread}
        getLabelById={getLabelById}
        colorClassMap={colorClassMap}
        unreadCount={unreadCount}
      />
      {/* Email Content */}
      <EmailContent
        selectedEmail={selectedEmail}
        darkMode={darkMode}
        activeFolder={activeFolder}
        emailSummary={emailSummary}
        summarizing={summarizing}
        getLabelById={getLabelById}
        lightBadgeClassMap={lightBadgeClassMap}
        darkBadgeClassMap={darkBadgeClassMap}
        toggleStarred={toggleStarred}
        toggleFlag={toggleFlag}
        replyToEmail={replyToEmail}
        forwardEmail={forwardEmail}
        deleteEmail={deleteEmail}
        summarizeEmail={summarizeEmail}
        printEmail={printEmail}
      />
      {/* Notification Panel */}
      <NotificationPanel
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        unreadNotifications={unreadNotifications}
        notifications={notifications}
        markAllNotificationsRead={markAllNotificationsRead}
      />
    </div>
  );
};
export default Home;

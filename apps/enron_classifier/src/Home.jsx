import React, { useState, useEffect } from 'react';
import {
  Star,
  Trash,
  File,
  Search,
  Archive,
  Filter,
  X,
  Reply,
  Forward,
  Flag,
  AlertCircle,
  Paperclip,
  MoreHorizontal,
  RefreshCcw,
  Eye,
  Printer,
  Download,
  Mail,
  FileText,
} from 'lucide-react';

import Sidebar from './components/Sidebar/Sidebar';
import NotificationPanel from './components/Notifications/Notificationpanel';

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
      {showToast && (
        <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center z-50 animate-pulse">
          <p>{toastMessage}</p>
          <button className="ml-2" onClick={() => setShowToast(false)}>
            <X size={14} />
          </button>
        </div>
      )}
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
      <div
        className={`w-1/3 ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r overflow-hidden flex flex-col transition-colors duration-300`}
      >
        <div
          className={`p-4 ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} border-b flex items-center justify-between`}
        >
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search emails..."
              className={`w-full pl-10 pr-4 py-2 ${
                darkMode
                  ? 'bg-gray-700 border-gray-600 text-gray-200 focus:ring-blue-400 placeholder-gray-400'
                  : 'bg-white border-gray-300 focus:ring-blue-500'
              } border rounded-lg focus:outline-none focus:ring-2 transition-all duration-300`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
          <button
            className={`ml-2 p-2 ${
              darkMode
                ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700'
                : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'
            } rounded-full transition-all duration-300 transform hover:rotate-180`}
            onClick={refreshEmails}
          >
            <RefreshCcw size={18} />
          </button>
        </div>

        {/* Filter bar */}
        <div
          className={`px-4 py-2 ${darkMode ? 'bg-gray-700 border-gray-700' : 'bg-gray-50 border-gray-200'} border-b flex items-center text-sm transition-colors duration-300`}
        >
          <div className="flex items-center">
            <Filter size={14} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
            <span className={`mr-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Filter:</span>
          </div>
          <button
            className={`mr-3 px-2 py-0.5 rounded transition-all duration-300 ${
              filterOptions.unreadOnly
                ? darkMode
                  ? 'bg-blue-800 text-blue-200'
                  : 'bg-blue-100 text-blue-600'
                : darkMode
                  ? 'text-gray-300'
                  : 'text-gray-600'
            }`}
            onClick={() => toggleFilterOption('unreadOnly')}
          >
            Unread
          </button>
          <button
            className={`mr-3 px-2 py-0.5 rounded transition-all duration-300 ${
              filterOptions.hasAttachments
                ? darkMode
                  ? 'bg-blue-800 text-blue-200'
                  : 'bg-blue-100 text-blue-600'
                : darkMode
                  ? 'text-gray-300'
                  : 'text-gray-600'
            }`}
            onClick={() => toggleFilterOption('hasAttachments')}
          >
            Attachments
          </button>
          <div className="ml-auto flex items-center">
            <span className={darkMode ? 'text-gray-300 mr-1' : 'text-gray-600 mr-1'}>Sort:</span>
            <select
              className={`${
                darkMode
                  ? 'bg-transparent border-none text-gray-300'
                  : 'bg-transparent border-none text-gray-600'
              } focus:outline-none text-sm transition-colors duration-300`}
              value={filterOptions.sortBy}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="date">Date</option>
              <option value="sender">Sender</option>
              <option value="subject">Subject</option>
            </select>
          </div>
        </div>

        {/* Email list container with overflow */}
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
                  ? `border-b border-gray-700 hover:bg-gray-700
                   ${!email.read ? 'bg-blue-900 bg-opacity-20' : ''}
                   ${selectedEmail?.id === email.id ? 'bg-gray-700' : ''}`
                  : `border-b border-gray-200 hover:bg-gray-50
                   ${!email.read ? 'bg-blue-50' : ''}
                   ${selectedEmail?.id === email.id ? 'bg-gray-100' : ''}`
              }`}
                  onClick={() => handleEmailClick(email)}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Priority indicator */}
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

                  {/* Email preview */}
                  <div className="flex items-start mt-1">
                    <p
                      className={`text-xs truncate flex-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
                    >
                      {email.content}
                    </p>

                    <div className="flex items-center space-x-1 ml-2">
                      {/* Label indicators */}
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

                      {/* Attachment indicator */}
                      {email.hasAttachments && (
                        <Paperclip
                          size={14}
                          className={darkMode ? 'text-gray-500' : 'text-gray-400'}
                        />
                      )}
                    </div>
                  </div>

                  {/* Email actions - visible on hover */}
                  <div
                    className={`absolute right-0 top-0 bottom-0 flex items-center justify-end px-2 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity duration-300 ${
                      darkMode
                        ? 'bg-gradient-to-l from-gray-800 via-gray-800 to-transparent'
                        : 'bg-gradient-to-l from-white via-white to-transparent'
                    }`}
                  >
                    <button
                      className={`p-1.5 rounded transform transition-transform hover:scale-110 ${
                        darkMode
                          ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700'
                          : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'
                      }`}
                      onClick={(e) => archiveEmail(email.id, e)}
                      title="Archive"
                    >
                      <Archive size={14} />
                    </button>
                    <button
                      className={`p-1.5 rounded transform transition-transform hover:scale-110 ${
                        darkMode
                          ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700'
                          : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'
                      }`}
                      onClick={(e) => deleteEmail(email.id, e)}
                      title="Delete"
                    >
                      <Trash size={14} />
                    </button>
                    <button
                      className={`p-1.5 rounded transform transition-transform hover:scale-110 ${
                        darkMode
                          ? 'text-gray-400 hover:text-blue-400 hover:bg-gray-700'
                          : 'text-gray-500 hover:text-blue-500 hover:bg-blue-50'
                      }`}
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

        {/* Status bar */}
        <div
          className={`px-4 py-2 ${darkMode ? 'bg-gray-700 border-gray-700 text-gray-300' : 'bg-gray-50 border-gray-200 text-gray-500'} border-t text-xs flex items-center transition-colors duration-300`}
        >
          <span>
            {emails.length} email{emails.length !== 1 ? 's' : ''}
          </span>
          <span className="mx-2">•</span>
          <span>{unreadCount} unread</span>
          <button
            className={`ml-auto flex items-center ${darkMode ? 'text-gray-400 hover:text-blue-400' : 'text-gray-500 hover:text-blue-500'} transition-colors duration-300`}
            onClick={refreshEmails}
          >
            <RefreshCcw
              size={12}
              className="mr-1 transform transition-transform hover:rotate-180"
            />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Email Content */}
      <div
        className={`flex-1 ${darkMode ? 'bg-gray-800' : 'bg-white'} flex flex-col transition-colors duration-300`}
      >
        {selectedEmail ? (
          <>
            {/* Email header */}
            <div
              className={`p-6 border-b ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} animate-fadeIn transition-colors duration-300`}
            >
              <div className="flex items-center justify-between mb-3">
                <h2 className={`text-xl font-bold ${darkMode ? 'text-gray-100' : ''}`}>
                  {selectedEmail.subject}
                </h2>
                <div className="flex items-center space-x-1">
                  {selectedEmail.labels.map((labelId) => {
                    const label = getLabelById(labelId);
                    const classes = darkMode
                      ? darkBadgeClassMap[label.name] || 'bg-gray-900 text-gray-200'
                      : lightBadgeClassMap[label.name] || 'bg-gray-100 text-gray-800';
                    return (
                      <span
                        key={labelId}
                        className={`px-2 py-0.5 text-xs font-medium rounded transition-colors duration-300 ${classes}`}
                      >
                        {label.name}
                      </span>
                    );
                  })}
                </div>
              </div>
              <div className="flex items-center">
                <div
                  className={`w-10 h-10 ${darkMode ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-600'} rounded-full flex items-center justify-center font-semibold transition-colors duration-300`}
                >
                  {(selectedEmail.sender || 'U')[0].toUpperCase()}
                </div>
                <div className="ml-3">
                  <div className="flex items-center">
                    <p className={`font-medium ${darkMode ? 'text-gray-200' : ''}`}>
                      {selectedEmail.sender || 'Unknown'}
                    </p>
                    <span className={`mx-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                      •
                    </span>
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
                  <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mt-0.5`}>
                    to me
                  </p>
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

            {/* Email content area with scrollable container */}
            <div
              className="flex-1 overflow-y-auto p-6 animate-fadeIn"
              style={{ animationDelay: '150ms' }}
            >
              {/* Email summary if available */}
              {emailSummary && (
                <div
                  className={`mb-4 p-4 rounded-lg ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-blue-50 text-gray-800'}`}
                >
                  <div className="flex items-center mb-2">
                    <FileText
                      size={16}
                      className={`mr-2 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}
                    />
                    <h3
                      className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}
                    >
                      Summary
                    </h3>
                  </div>
                  <p className="text-sm">{emailSummary}</p>
                </div>
              )}

              {/* Email body */}
              <div className="py-4 whitespace-pre-line mb-4">
                <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>
                  {selectedEmail.content}
                </p>
                <p className={`mt-6 ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
                  Best regards,
                </p>
                <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>
                  {selectedEmail.sender || 'Unknown'}
                </p>
              </div>

              {/* Attachments section */}
              {selectedEmail.attachments && selectedEmail.attachments.length > 0 && (
                <div
                  className={`mt-6 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'} pt-4 animate-fadeIn`}
                  style={{ animationDelay: '300ms' }}
                >
                  <h3
                    className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-3 animate-slideUp`}
                    style={{ animationDelay: '350ms' }}
                  >
                    Attachments ({selectedEmail.attachments.length})
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {selectedEmail.attachments.map((attachment, index) => (
                      <div
                        key={index}
                        className={`flex items-center p-3 border rounded-lg ${
                          darkMode
                            ? 'border-gray-700 bg-gray-700 hover:bg-gray-600'
                            : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                        } transition-all duration-300 transform hover:scale-105 hover:shadow-md animate-fadeIn`}
                        style={{ animationDelay: `${400 + index * 100}ms` }}
                      >
                        {attachment.type === 'pdf' && (
                          <div
                            className={`w-8 h-8 rounded flex items-center justify-center mr-3 ${
                              darkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-500'
                            } transform transition-transform group-hover:rotate-3`}
                          >
                            <File
                              size={16}
                              className="transition-all duration-300 transform group-hover:scale-110"
                            />
                          </div>
                        )}
                        {attachment.type === 'image' && (
                          <div
                            className={`w-8 h-8 rounded flex items-center justify-center mr-3 ${
                              darkMode ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-500'
                            } transform transition-transform group-hover:rotate-3`}
                          >
                            <File
                              size={16}
                              className="transition-all duration-300 transform group-hover:scale-110"
                            />
                          </div>
                        )}
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
                            darkMode
                              ? 'text-gray-400 hover:text-blue-300'
                              : 'text-gray-500 hover:text-blue-500'
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
              )}
            </div>

            {/* Email actions footer */}
            <div
              className={`p-4 border-t ${darkMode ? 'border-gray-700 bg-gray-700' : 'border-gray-200 bg-gray-50'} flex animate-fadeIn`}
              style={{ animationDelay: '500ms' }}
            >
              <div className="flex space-x-2">
                <button
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center shadow-sm transition-all duration-300 transform hover:scale-105 hover:shadow animate-slideUp"
                  onClick={replyToEmail}
                  style={{ animationDelay: '550ms' }}
                >
                  <Reply
                    size={16}
                    className="mr-2 transform transition-transform group-hover:rotate-45"
                  />
                  Reply
                </button>
                <button
                  className={`px-4 py-2 border rounded-lg flex items-center transition-all duration-300 transform hover:scale-105 animate-slideUp ${
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
                  className={`px-4 py-2 border rounded-lg flex items-center transition-all duration-300 transform hover:scale-105 animate-slideUp ${
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
                  <Printer
                    size={16}
                    className="transform transition-transform hover:translate-y-0.5"
                  />
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
                  <MoreHorizontal
                    size={16}
                    className="transform transition-transform hover:rotate-90"
                  />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div
            className={`flex flex-col items-center justify-center h-full ${darkMode ? 'text-gray-400' : 'text-gray-500'} animate-fadeIn`}
          >
            <Mail size={64} strokeWidth={1} className="animate-pulse transition-all duration-500" />
            <p
              className={`mt-4 text-lg ${darkMode ? 'text-gray-300' : ''} animate-slideUp`}
              style={{ animationDelay: '200ms' }}
            >
              Select an email to read
            </p>
            <p
              className={`text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'} mt-2 animate-slideUp`}
              style={{ animationDelay: '300ms' }}
            >
              {activeFolder === 'inbox'
                ? 'Your inbox is organized and ready for you'
                : `Viewing your ${activeFolder} folder`}
            </p>
          </div>
        )}
      </div>

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

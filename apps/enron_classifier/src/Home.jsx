import React, { useState, useEffect } from 'react';
import { Inbox, Send, Star, Trash, File, Menu, Search, Settings, Bell, User } from 'lucide-react';
import UserSelector from './UserSelector';

const Home = () => {
  // Add state for users and folders
  const [currentUser, setCurrentUser] = useState(null);
  const [folders, setFolders] = useState([]);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [loading, setLoading] = useState(true);

  // Fetch folders when user changes
  useEffect(() => {
    if (currentUser) {
      fetchFolders(currentUser.username);
      setSelectedEmail(null);
    }
  }, [currentUser]);

  // Fetch emails when folder changes
  useEffect(() => {
    if (currentUser && activeFolder) {
      fetchEmails(currentUser.username, activeFolder);
    }
  }, [currentUser, activeFolder]);

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
    }
  };

  const fetchEmails = async (username, folder) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:5050/api/users/${username}/folders/${folder}/emails`
      );
      if (response.ok) {
        const data = await response.json();
        // Transform the data to match our component's expected format
        const formattedEmails = data.map((email) => ({
          id: email.id,
          sender: email.from_address,
          subject: email.subject || '(No Subject)',
          content: email.body,
          read: Math.random() > 0.5, // Mock read status since it's not in the DB
          starred: Math.random() > 0.7, // Mock starred status
          time: formatDate(email.date),
        }));
        setEmails(formattedEmails);
      }
    } catch (error) {
      console.error('Error fetching emails:', error);
    }
    setLoading(false);
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
    // Mark as read (in a real app, you'd update this in the database)
    setEmails(emails.map((e) => (e.id === email.id ? { ...e, read: true } : e)));
  };

  const toggleStarred = (id, e) => {
    e.stopPropagation();
    setEmails(
      emails.map((email) => (email.id === id ? { ...email, starred: !email.starred } : email))
    );
  };

  const handleSelectUser = (user) => {
    setCurrentUser(user);
    setSelectedEmail(null);
  };

  const handleSelectFolder = (folder) => {
    setActiveFolder(folder);
    setSelectedEmail(null);
  };

  // Count unread emails
  const unreadCount = emails.filter((email) => !email.read).length;

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-600">EnronBox</h1>
          <button className="text-gray-500">
            <Menu size={20} />
          </button>
        </div>

        {/* User Selector */}
        <div className="px-4 mb-4">
          <UserSelector onSelectUser={handleSelectUser} currentUser={currentUser} />
        </div>

        <button className="mx-4 my-2 bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center justify-center">
          <span>Compose</span>
        </button>

        <nav className="mt-6 flex-1 overflow-y-auto">
          <ul>
            {folders.map((folder) => (
              <li
                key={folder}
                className={`flex items-center px-4 py-2 cursor-pointer ${
                  activeFolder === folder ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                }`}
                onClick={() => handleSelectFolder(folder)}
              >
                {folder.toLowerCase() === 'inbox' && <Inbox size={18} className="mr-3" />}
                {folder.toLowerCase() === 'sent' && <Send size={18} className="mr-3" />}
                {folder.toLowerCase() === 'starred' && <Star size={18} className="mr-3" />}
                {folder.toLowerCase() === 'drafts' && <File size={18} className="mr-3" />}
                {folder.toLowerCase() === 'trash' && <Trash size={18} className="mr-3" />}
                {!['inbox', 'sent', 'starred', 'drafts', 'trash'].includes(
                  folder.toLowerCase()
                ) && <File size={18} className="mr-3" />}
                <span>{folder}</span>
                {folder.toLowerCase() === 'inbox' && unreadCount > 0 && (
                  <span className="ml-auto bg-blue-500 text-white text-xs font-medium px-2 py-1 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white">
              <User size={16} />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">{currentUser?.username || 'No User'}</p>
              <p className="text-xs text-gray-500">
                {currentUser ? `${currentUser.username}@enron.com` : ''}
              </p>
            </div>
            <button className="ml-auto text-gray-500">
              <Settings size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Email List */}
      <div className="w-1/3 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <input
              type="text"
              placeholder="Search emails..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center p-8">
            <p className="text-gray-500">Loading emails...</p>
          </div>
        ) : emails.length === 0 ? (
          <div className="flex justify-center items-center p-8">
            <p className="text-gray-500">No emails in this folder</p>
          </div>
        ) : (
          <div>
            {emails.map((email) => (
              <div
                key={email.id}
                className={`p-4 border-b border-gray-200 cursor-pointer ${!email.read ? 'bg-blue-50' : ''} ${selectedEmail?.id === email.id ? 'bg-gray-100' : ''}`}
                onClick={() => handleEmailClick(email)}
              >
                <div className="flex items-center mb-1">
                  <span className={`font-medium ${!email.read ? 'font-semibold' : ''}`}>
                    {email.sender || 'Unknown'}
                  </span>
                  <span className="ml-auto text-xs text-gray-500">{email.time}</span>
                </div>
                <div className="flex items-center">
                  <h3 className={`text-sm ${!email.read ? 'font-semibold' : ''}`}>
                    {email.subject}
                  </h3>
                  <button
                    className={`ml-auto ${email.starred ? 'text-yellow-400' : 'text-gray-400'}`}
                    onClick={(e) => toggleStarred(email.id, e)}
                  >
                    <Star size={16} fill={email.starred ? 'currentColor' : 'none'} />
                  </button>
                </div>
                <p className="text-xs text-gray-500 truncate mt-1">{email.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Email Content */}
      <div className="flex-1 bg-white p-6 overflow-y-auto">
        {selectedEmail ? (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-2">{selectedEmail.subject}</h2>
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  {(selectedEmail.sender || 'U')[0].toUpperCase()}
                </div>
                <div className="ml-3">
                  <p className="font-medium">{selectedEmail.sender || 'Unknown'}</p>
                  <p className="text-xs text-gray-500">to me</p>
                </div>
                <p className="ml-auto text-sm text-gray-500">{selectedEmail.time}</p>
              </div>
              <div className="py-4 border-t border-b border-gray-200 whitespace-pre-line">
                <p className="text-gray-800">{selectedEmail.content}</p>
                <p className="mt-4 text-gray-800">Best regards,</p>
                <p className="text-gray-800">{selectedEmail.sender || 'Unknown'}</p>
              </div>
              <div className="mt-4 flex space-x-3">
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                    />
                  </svg>
                  Reply
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                  Forward
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 flex items-center">
                  <Trash className="h-4 w-4 mr-2" />
                  Delete
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Inbox size={64} strokeWidth={1} />
            <p className="mt-4 text-lg">Select an email to read</p>
          </div>
        )}
      </div>

      {/* Notification Panel */}
      <div className="w-12 bg-gray-800 flex flex-col items-center py-4">
        <button className="w-8 h-8 mb-6 text-gray-400 hover:text-white">
          <Bell size={20} />
        </button>
        <button className="w-8 h-8 text-gray-400 hover:text-white">
          <Settings size={20} />
        </button>
      </div>
    </div>
  );
};

export default Home;

import React, { useState } from 'react';
import { Inbox, Send, Star, Trash, File, Menu, Search, Settings, Bell, User } from 'lucide-react';

const Home = () => {
  const [emails, setEmails] = useState([
    {
      id: 1,
      sender: 'John Doe',
      subject: 'Meeting Tomorrow',
      content: 'Hi there, just confirming our meeting tomorrow at 2pm.',
      read: false,
      starred: false,
      time: '10:30 AM',
    },
    {
      id: 2,
      sender: 'Jane Smith',
      subject: 'Project Update',
      content: "Here's the latest update on our current project. We're making good progress!",
      read: true,
      starred: true,
      time: '9:15 AM',
    },
    {
      id: 3,
      sender: 'Alex Johnson',
      subject: 'Lunch Next Week?',
      content: "Would you like to grab lunch next week? I'm free on Tuesday.",
      read: true,
      starred: false,
      time: 'Yesterday',
    },
    {
      id: 4,
      sender: 'Sarah Wilson',
      subject: 'Invoice #1234',
      content: "Please find attached the invoice for last month's services.",
      read: false,
      starred: false,
      time: 'Yesterday',
    },
    {
      id: 5,
      sender: 'Michael Brown',
      subject: 'New Product Launch',
      content: "We're excited to announce our new product launch next month!",
      read: true,
      starred: false,
      time: 'Apr 15',
    },
  ]);

  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeSidebar, setActiveSidebar] = useState('inbox');

  const handleEmailClick = (email) => {
    setSelectedEmail(email);
    // Mark as read
    setEmails(emails.map((e) => (e.id === email.id ? { ...e, read: true } : e)));
  };

  const toggleStarred = (id, e) => {
    e.stopPropagation();
    setEmails(
      emails.map((email) => (email.id === id ? { ...email, starred: !email.starred } : email))
    );
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-600">MailBox</h1>
          <button className="text-gray-500">
            <Menu size={20} />
          </button>
        </div>

        <button className="mx-4 my-2 bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center justify-center">
          <span>Compose</span>
        </button>

        <nav className="mt-6 flex-1">
          <ul>
            <li
              className={`flex items-center px-4 py-2 ${activeSidebar === 'inbox' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`}
              onClick={() => setActiveSidebar('inbox')}
            >
              <Inbox size={18} className="mr-3" />
              <span>Inbox</span>
              <span className="ml-auto bg-blue-500 text-white text-xs font-medium px-2 py-1 rounded-full">
                2
              </span>
            </li>
            <li
              className={`flex items-center px-4 py-2 ${activeSidebar === 'starred' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`}
              onClick={() => setActiveSidebar('starred')}
            >
              <Star size={18} className="mr-3" />
              <span>Starred</span>
            </li>
            <li
              className={`flex items-center px-4 py-2 ${activeSidebar === 'sent' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`}
              onClick={() => setActiveSidebar('sent')}
            >
              <Send size={18} className="mr-3" />
              <span>Sent</span>
            </li>
            <li
              className={`flex items-center px-4 py-2 ${activeSidebar === 'drafts' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`}
              onClick={() => setActiveSidebar('drafts')}
            >
              <File size={18} className="mr-3" />
              <span>Drafts</span>
            </li>
            <li
              className={`flex items-center px-4 py-2 ${activeSidebar === 'trash' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}`}
              onClick={() => setActiveSidebar('trash')}
            >
              <Trash size={18} className="mr-3" />
              <span>Trash</span>
            </li>
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white">
              <User size={16} />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">User Name</p>
              <p className="text-xs text-gray-500">user@example.com</p>
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

        <div>
          {emails.map((email) => (
            <div
              key={email.id}
              className={`p-4 border-b border-gray-200 cursor-pointer ${!email.read ? 'bg-blue-50' : ''} ${selectedEmail?.id === email.id ? 'bg-gray-100' : ''}`}
              onClick={() => handleEmailClick(email)}
            >
              <div className="flex items-center mb-1">
                <span className={`font-medium ${!email.read ? 'font-semibold' : ''}`}>
                  {email.sender}
                </span>
                <span className="ml-auto text-xs text-gray-500">{email.time}</span>
              </div>
              <div className="flex items-center">
                <h3 className={`text-sm ${!email.read ? 'font-semibold' : ''}`}>{email.subject}</h3>
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
      </div>

      {/* Email Content */}
      <div className="flex-1 bg-white p-6 overflow-y-auto">
        {selectedEmail ? (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-2">{selectedEmail.subject}</h2>
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  {selectedEmail.sender.charAt(0)}
                </div>
                <div className="ml-3">
                  <p className="font-medium">{selectedEmail.sender}</p>
                  <p className="text-xs text-gray-500">to me</p>
                </div>
                <p className="ml-auto text-sm text-gray-500">{selectedEmail.time}</p>
              </div>
              <div className="py-4 border-t border-b border-gray-200">
                <p className="text-gray-800">{selectedEmail.content}</p>
                <p className="mt-4 text-gray-800">Best regards,</p>
                <p className="text-gray-800">{selectedEmail.sender}</p>
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

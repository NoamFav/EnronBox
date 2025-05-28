import React, { useState, useEffect } from 'react';
import { ChevronDown, Users, User, Check, Loader2 } from 'lucide-react';

const UserSelector = ({ onSelectUser, currentUser, darkMode }) => {
  const [users, setUsers] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Fetch users from API
    const fetchUsers = async () => {
      try {
        const response = await fetch('http://localhost:5050/api/users');
        if (response.ok) {
          const data = await response.json();
          setUsers(data);
          // Select first user if none selected
          if (!currentUser && data.length > 0) {
            onSelectUser(data[0]);
          }
        } else {
          console.error('Failed to fetch users');
        }
        setLoading(false);
      } catch (error) {
        console.error('Error fetching users:', error);
        setLoading(false);
      }
    };

    fetchUsers();
  }, [currentUser, onSelectUser]);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleSelectUser = (user) => {
    onSelectUser(user);
    setIsOpen(false);
    setSearchTerm('');
  };

  const filteredUsers = users.filter((user) =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div
        className={`flex items-center space-x-3 px-3 py-2 rounded-lg ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-50 text-gray-600'} transition-all duration-150`}
      >
        <Loader2 size={16} className="animate-spin" />
        <span className="text-sm">Loading users...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className={`
          flex items-center justify-between w-full px-3 py-2 text-sm font-medium
          transition-all duration-150 shadow-sm hover:shadow
          ${
            isOpen
              ? darkMode
                ? 'bg-gray-700 text-gray-200 border border-gray-600 rounded-t-lg'
                : 'bg-white text-gray-700 border border-gray-300 rounded-t-lg'
              : darkMode
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-200 border border-gray-600 hover:border-gray-500 rounded-lg'
                : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 hover:border-gray-400 rounded-lg'
          }
          ${isOpen ? (darkMode ? 'ring-2 ring-blue-500' : 'ring-2 ring-blue-400') : ''}
        `}
      >
        <div className="flex items-center">
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${darkMode ? 'bg-blue-600' : 'bg-blue-500'} text-white`}
          >
            <User size={12} />
          </div>
          <span className="truncate">{currentUser?.username || 'Select User'}</span>
        </div>
        <ChevronDown
          size={16}
          className={`ml-2 transition-transform duration-300 ${
            isOpen ? 'transform rotate-180' : ''
          } ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div
            className={`
            absolute z-20 w-full mt-1 rounded-b-lg overflow-hidden shadow-lg border-l border-r border-b animate-fadeIn
            ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}
          `}
          >
            {/* Search Input */}
            <div className={`p-3 border-b ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={`
                  w-full px-3 py-2 text-sm rounded-md border
                  ${
                    darkMode
                      ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400 focus:border-blue-500'
                      : 'bg-gray-50 border-gray-300 text-gray-700 placeholder-gray-500 focus:border-blue-400'
                  }
                  focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50
                `}
                autoFocus
              />
            </div>

            {/* Users List */}
            <div className="max-h-60 overflow-y-auto">
              {filteredUsers.length > 0 ? (
                <ul className="py-1">
                  {filteredUsers.map((user) => (
                    <li
                      key={user.id}
                      className={`
                        flex items-center px-3 py-2 cursor-pointer
                        transition-colors duration-150
                        ${
                          darkMode
                            ? 'hover:bg-gray-700 text-gray-200'
                            : 'hover:bg-blue-50 text-gray-700'
                        }
                        ${
                          currentUser?.id === user.id
                            ? darkMode
                              ? 'bg-gray-700'
                              : 'bg-blue-50'
                            : ''
                        }
                      `}
                      onClick={() => handleSelectUser(user)}
                    >
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                          currentUser?.id === user.id
                            ? darkMode
                              ? 'bg-blue-600'
                              : 'bg-blue-500'
                            : darkMode
                              ? 'bg-gray-600'
                              : 'bg-gray-400'
                        } text-white`}
                      >
                        <User size={12} />
                      </div>
                      <span className="flex-1 text-sm">{user.username}</span>
                      {currentUser?.id === user.id && (
                        <Check size={16} className={darkMode ? 'text-blue-400' : 'text-blue-500'} />
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <div
                  className={`px-4 py-6 text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
                >
                  <Users size={24} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No users found</p>
                </div>
              )}
            </div>

            {/* Footer with user count */}
            <div
              className={`px-3 py-2 text-xs border-t ${
                darkMode
                  ? 'border-gray-600 text-gray-400 bg-gray-700'
                  : 'border-gray-300 text-gray-500 bg-white'
              }`}
            >
              {filteredUsers.length} of {users.length} users
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default UserSelector;

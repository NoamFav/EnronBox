import React, { useState, useEffect } from 'react';
import { ChevronDown, Users } from 'lucide-react';

const UserSelector = ({ onSelectUser, currentUser }) => {
  const [users, setUsers] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

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
  }, []);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleSelectUser = (user) => {
    onSelectUser(user);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <Users size={16} />
        <span>Loading users...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className="flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div className="flex items-center">
          <Users size={16} className="mr-2" />
          <span>{currentUser?.username || 'Select User'}</span>
        </div>
        <ChevronDown
          size={16}
          className={`ml-2 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
          <ul className="py-1 overflow-auto max-h-60">
            {users.map((user) => (
              <li
                key={user.id}
                className={`px-3 py-2 text-sm cursor-pointer hover:bg-blue-50 ${
                  currentUser?.id === user.id ? 'bg-blue-100' : ''
                }`}
                onClick={() => handleSelectUser(user)}
              >
                {user.username}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default UserSelector;

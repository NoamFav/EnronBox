import {
  Calendar,
  Clock,
  Bookmark,
  Sun,
  Moon,
  Settings,
  User,
  X,
  AlertTriangle,
} from 'lucide-react';
import Bell from './Bell';

const Panel = ({
  darkMode,
  toggleDarkMode,
  showNotifications,
  setShowNotifications,
  unreadNotifications,
  notifications,
  markAllNotificationsRead,
}) => {
  return (
    <>
      {/* Notification Panel */}
      <div
        className={`w-16 ${darkMode ? 'bg-gray-900' : 'bg-gray-800'} flex flex-col items-center py-6 animate-fadeIn`}
        style={{ animationDelay: '400ms' }}
      >
        <Bell
          showNotifications={showNotifications}
          setShowNotifications={setShowNotifications}
          unreadNotifications={unreadNotifications}
        />

        <button className="w-10 h-10 mb-4 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110">
          <Calendar size={20} className="transition-transform duration-300 hover:rotate-12" />
        </button>
        <button className="w-10 h-10 mb-4 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110">
          <Clock size={20} className="transition-transform duration-300 hover:rotate-45" />
        </button>
        <button className="w-10 h-10 mb-4 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110">
          <Bookmark size={20} className="transition-transform duration-300 hover:translate-y-1" />
        </button>
        <button
          className="w-10 h-10 mb-4 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110 hover:rotate-12"
          onClick={toggleDarkMode}
          title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {darkMode ? (
            <Sun size={20} className="animate-spin-slow" />
          ) : (
            <Moon size={20} className="animate-pulse" />
          )}
        </button>
        <button className="w-10 h-10 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110">
          <Settings size={20} className="transition-transform duration-300 hover:rotate-90" />
        </button>

        <div className="mt-auto">
          <button className="w-10 h-10 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110">
            <User size={20} className="transition-transform duration-300 hover:scale-125" />
          </button>
        </div>
      </div>

      {/* Notifications panel */}
      {showNotifications && (
        <div
          className={`absolute right-16 top-0 w-72 ${darkMode ? 'bg-gray-800 shadow-xl border-gray-700' : 'bg-white shadow-lg border-gray-200'} rounded-lg mt-4 mr-4 z-10 border animate-slideInRight`}
        >
          <div
            className={`p-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'} flex items-center justify-between`}
          >
            <h3
              className={`font-medium ${darkMode ? 'text-gray-200' : ''} animate-fadeIn`}
              style={{ animationDelay: '100ms' }}
            >
              Notifications
            </h3>
            <div className="flex items-center">
              <button
                className={`text-sm ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-500 hover:text-blue-700'} transition-colors duration-300`}
                onClick={markAllNotificationsRead}
              >
                Mark all read
              </button>
              <button
                className={`ml-2 ${darkMode ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'} transition-all duration-300 transform hover:rotate-90`}
                onClick={() => setShowNotifications(false)}
              >
                <X size={16} />
              </button>
            </div>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div
                className={`p-4 text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'} animate-fadeIn`}
                style={{ animationDelay: '200ms' }}
              >
                <p>No notifications</p>
              </div>
            ) : (
              notifications.map((notification, index) => (
                <div
                  key={notification.id}
                  className={`p-3 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'} ${
                    darkMode
                      ? !notification.read
                        ? 'bg-blue-900 bg-opacity-20 hover:bg-gray-700'
                        : 'hover:bg-gray-700'
                      : !notification.read
                        ? 'bg-blue-50 hover:bg-gray-50'
                        : 'hover:bg-gray-50'
                  } transition-colors duration-300 animate-fadeIn`}
                  style={{ animationDelay: `${200 + index * 100}ms` }}
                >
                  <div className="flex">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        !notification.read
                          ? darkMode
                            ? 'bg-blue-900 text-blue-300'
                            : 'bg-blue-100 text-blue-500'
                          : darkMode
                            ? 'bg-gray-700 text-gray-400'
                            : 'bg-gray-100 text-gray-500'
                      } transform transition-transform duration-300 hover:scale-110 ${!notification.read ? 'animate-bounce-mini' : ''}`}
                    >
                      <AlertTriangle size={16} />
                    </div>
                    <div className="ml-3">
                      <p
                        className={`text-sm ${
                          darkMode ? 'text-gray-300' : ''
                        } ${!notification.read ? 'font-medium' : ''} transition-colors duration-300`}
                      >
                        {notification.text}
                      </p>
                      <p
                        className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'} mt-1 animate-slideUp`}
                        style={{ animationDelay: `${300 + index * 100}ms` }}
                      >
                        2 hours ago
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          <div
            className={`p-3 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'} text-center animate-fadeIn`}
            style={{ animationDelay: '400ms' }}
          >
            <button
              className={`text-sm ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-500 hover:text-blue-700'} transition-colors duration-300 transform hover:scale-105`}
            >
              View all notifications
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Panel;

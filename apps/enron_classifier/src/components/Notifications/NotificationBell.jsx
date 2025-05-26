import { Bell } from 'lucide-react';

const NotificationBell = ({ showNotifications, setShowNotifications, unreadNotifications }) => {
  return (
    <div className="relative">
      <button
        className="w-10 h-10 mb-6 text-gray-400 hover:text-white flex items-center justify-center transition-all duration-300 transform hover:scale-110"
        onClick={() => setShowNotifications(!showNotifications)}
      >
        <Bell size={20} className={unreadNotifications > 0 ? 'animate-swing' : ''} />
        {unreadNotifications > 0 && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
            <span className="text-white text-xs">{unreadNotifications}</span>
          </div>
        )}
      </button>
    </div>
  );
};

export default NotificationBell;

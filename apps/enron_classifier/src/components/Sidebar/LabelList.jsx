import React from 'react';
import { ChevronDown, Tag } from 'lucide-react';

const LabelList = ({
  labels,
  showLabels,
  setShowLabels,
  filterOptions,
  toggleFilterByLabel,
  colorClassMap,
  darkMode,
}) => {
  return (
    <>
      {/* Labels Toggle Header */}
      <div
        className={`flex items-center justify-between px-4 py-1 mt-3 cursor-pointer ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors duration-150`}
        onClick={() => setShowLabels(!showLabels)}
      >
        <p
          className={`text-xs font-semibold ${darkMode ? 'text-gray-400' : 'text-gray-500'} uppercase tracking-wider`}
        >
          Labels
        </p>
        <div
          className={`transform transition-transform duration-300 ${showLabels ? 'rotate-180' : 'rotate-0'} ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
        >
          <ChevronDown size={14} />
        </div>
      </div>

      {/* Labels List */}
      {showLabels && (
        <ul className="ml-2 animate-fadeIn">
          {labels.map((label) => {
            const isActive = filterOptions.byLabel === label.name;
            const dotClass = colorClassMap[label.name] || 'bg-gray-500';
            return (
              <li
                key={label.id}
                onClick={() => toggleFilterByLabel(label.name)}
                className={`
                  flex items-center px-4 py-2 cursor-pointer
                  transition-colors duration-150
                  ${
                    darkMode
                      ? isActive
                        ? 'bg-gray-600 text-white'
                        : 'hover:bg-gray-700 text-gray-300'
                      : isActive
                        ? 'bg-gray-200 text-gray-900'
                        : 'hover:bg-gray-100 text-gray-700'
                  }
                `}
              >
                <div className={`w-3 h-3 rounded-full ${dotClass} mr-3`} />
                <span className="text-sm">{label.name}</span>
              </li>
            );
          })}
          <li
            className={`flex items-center px-4 py-2 cursor-pointer ${darkMode ? 'hover:bg-gray-700 text-blue-400' : 'hover:bg-gray-100 text-blue-500'} transition-colors duration-150`}
          >
            <Tag size={14} className="mr-3" />
            <span className="text-sm">Manage labels</span>
          </li>
        </ul>
      )}
    </>
  );
};

export default LabelList;

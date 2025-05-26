import React from 'react';

const Labels = ({ labels, getLabelById, lightBadgeClassMap, darkBadgeClassMap, darkMode }) => {
  return (
    <div className="flex items-center space-x-1">
      {labels.map((labelId) => {
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
  );
};

export default Labels;

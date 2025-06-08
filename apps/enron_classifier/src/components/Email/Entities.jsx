import React from 'react';
import { Tag } from 'lucide-react';

const Entities = ({ entities, darkMode }) => {
  if (!entities || Object.keys(entities).length === 0) return null;

  return (
    <div
      className={`mb-4 p-4 rounded-lg ${
        darkMode ? 'bg-gray-700 text-gray-300' : 'bg-green-50 text-gray-800'
      }`}
    >
      <div className="flex items-center mb-2">
        <Tag
          size={16}
          className={`mr-2 ${darkMode ? 'text-green-400' : 'text-green-600'}`}
        />
        <h3
          className={`text-sm font-medium ${
            darkMode ? 'text-gray-200' : 'text-gray-700'
          }`}
        >
          Entities
        </h3>
      </div>

      <ul className="text-sm space-y-1">
        {Object.entries(entities).map(([label, values]) =>
          values.length ? (
            <li key={label}>
              <span className="font-semibold capitalize">{label}:</span>{' '}
              {values.join(', ')}
            </li>
          ) : null
        )}
      </ul>
    </div>
  );
};

export default Entities;

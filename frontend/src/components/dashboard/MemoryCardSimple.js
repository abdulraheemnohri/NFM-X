import React from 'react';

const MemoryCardSimple = ({ memory, onClick }) => {
  return React.createElement('div', {
    className: 'border rounded p-4 bg-white shadow cursor-pointer',
    onClick: () => onClick && onClick(memory)
  }, [
    React.createElement('p', { className: 'text-sm text-gray-800', key: 'content' }, memory.content),
    React.createElement('div', { className: 'text-xs text-gray-500 mt-2', key: 'id' }, 'ID: ' + memory.id)
  ]);
};

export default MemoryCardSimple;
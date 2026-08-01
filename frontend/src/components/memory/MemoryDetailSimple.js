import React from 'react';

const MemoryDetailSimple = ({ memory, onClose }) => {
  if (!memory) return null;
  
  return React.createElement('div', {
    className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'
  }, [
    React.createElement('div', {
      className: 'bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto'
    }, [
      React.createElement('div', { className: 'p-6' }, [
        React.createElement('div', { className: 'flex justify-between items-start mb-4', key: 'header' }, [
          React.createElement('h2', { className: 'text-xl font-bold', key: 'title' }, 'Memory: ' + memory.id),
          React.createElement('button', {
            className: 'text-gray-400 hover:text-gray-600 text-2xl',
            key: 'close',
            onClick: onClose
          }, 'X')
        ]),
        React.createElement('div', { className: 'space-y-4', key: 'content' }, [
          React.createElement('div', { key: 'type' }, [
            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Type'),
            React.createElement('p', { className: 'text-sm text-gray-800' }, memory.type)
          ]),
          React.createElement('div', { key: 'status' }, [
            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Status'),
            React.createElement('p', { className: 'text-sm text-gray-800' }, memory.status)
          ]),
          React.createElement('div', { key: 'content' }, [
            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Content'),
            React.createElement('p', { className: 'text-sm text-gray-800' }, memory.content)
          ]),
          React.createElement('button', {
            className: 'mt-4 px-4 py-2 bg-blue-600 text-white rounded',
            key: 'close-btn',
            onClick: onClose
          }, 'Close')
        ])
      ])
    ])
  ]);
};

export default MemoryDetailSimple;
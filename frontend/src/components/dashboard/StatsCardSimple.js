import React from 'react';

const StatsCardSimple = ({ title, value, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
  };
  const bgColor = colorClasses[color || 'blue'];
  
  return React.createElement('div', { className: 'bg-white rounded shadow p-4' }, [
    React.createElement('div', { className: 'flex items-center', key: 'container' }, [
      React.createElement('div', { className: `w-8 h-8 rounded-lg ${bgColor} mr-3`, key: 'color-box' }),
      React.createElement('div', { key: 'content' }, [
        React.createElement('p', { className: 'text-sm text-gray-500', key: 'title' }, title),
        React.createElement('p', { className: 'text-xl font-bold', key: 'value' }, value)
      ])
    ])
  ]);
};

export default StatsCardSimple;
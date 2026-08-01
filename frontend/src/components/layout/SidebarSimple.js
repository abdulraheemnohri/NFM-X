import React from 'react';
import { NavLink } from 'react-router-dom';

const SidebarSimple = () => {
  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Memories', path: '/memories' },
    { name: 'Knowledge Graph', path: '/graph' },
    { name: 'Search', path: '/search' },
    { name: 'OCR', path: '/ocr' },
    { name: 'Analytics', path: '/analytics' },
    { name: 'Settings', path: '/settings' },
  ];

  const items = navItems.map((item) => (
    React.createElement('li', { key: item.path }, [
      React.createElement(NavLink, {
        to: item.path,
        className: ({ isActive }) =>
          `flex items-center space-x-3 px-3 py-2 rounded-md ${isActive ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`
      }, [
        React.createElement('span', { className: 'text-sm' }, item.name)
      ])
    ])
  ));

  return React.createElement('div', { className: 'w-64 bg-gray-50 border-r h-screen' }, [
    React.createElement('div', { className: 'p-4' }, [
      React.createElement('h2', { className: 'text-xl font-bold text-gray-800' }, 'NFM-X'),
      React.createElement('p', { className: 'text-sm text-gray-500' }, 'Memory Layer')
    ]),
    React.createElement('nav', { className: 'p-4' }, [
      React.createElement('ul', { className: 'space-y-2' }, items)
    ])
  ]);
};

export default SidebarSimple;
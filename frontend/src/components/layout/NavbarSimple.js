import React from 'react';
import { Link } from 'react-router-dom';

const NavbarSimple = () => {
  return React.createElement('nav', { className: 'bg-white shadow-sm border-b' }, [
    React.createElement('div', { className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8' }, [
      React.createElement('div', { className: 'flex justify-between h-16 items-center' }, [
        React.createElement(Link, { to: '/', className: 'flex items-center space-x-2' }, [
          React.createElement('div', { className: 'w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center' }, [
            React.createElement('span', { className: 'text-white font-bold text-sm' }, 'NFM')
          ]),
          React.createElement('span', { className: 'text-xl font-bold text-gray-800' }, 'NFM-X')
        ]),
        React.createElement('div', { className: 'flex items-center space-x-6' }, [
          React.createElement(Link, { to: '/', className: 'text-gray-600 hover:text-gray-900' }, 'Dashboard'),
          React.createElement(Link, { to: '/memories', className: 'text-gray-600 hover:text-gray-900' }, 'Memories'),
          React.createElement(Link, { to: '/graph', className: 'text-gray-600 hover:text-gray-900' }, 'Graph'),
          React.createElement(Link, { to: '/settings', className: 'text-gray-600 hover:text-gray-900' }, 'Settings')
        ])
      ])
    ])
  ]);
};

export default NavbarSimple;
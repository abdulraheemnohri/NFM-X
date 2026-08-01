import React from 'react';
import MemoryCardSimple from '../dashboard/MemoryCardSimple';

const MemoryListSimple = ({ memories, onMemoryClick }) => {
  if (!memories || memories.length === 0) {
    return React.createElement('div', {
      className: 'text-center py-8 text-gray-500'
    }, 'No memories found');
  }
  
  const cards = memories.map((memory) => (
    React.createElement(MemoryCardSimple, {
      key: memory.id,
      memory: memory,
      onClick: onMemoryClick
    })
  ));
  
  return React.createElement('div', {
    className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
  }, cards);
};

export default MemoryListSimple;
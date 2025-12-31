import React from 'react';
import './GridLayout.css';

const GridLayout = ({ children, columns = 2, gap = '24px' }) => {
  const style = {
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: gap,
  };

  return (
    <div className="grid-layout" style={style}>
      {children}
    </div>
  );
};

export const GridItem = ({ children, span = 1, className = '' }) => {
  const style = {
    gridColumn: `span ${span}`,
  };

  return (
    <div className={`grid-item ${className}`} style={style}>
      {children}
    </div>
  );
};

export default GridLayout;

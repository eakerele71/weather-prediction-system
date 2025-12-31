import React from 'react';
import './Header.css';

const Header = ({ title, subtitle, children }) => {
  return (
    <header className="app-header">
      <div className="container">
        <div className="header-content">
          <div className="header-text">
            <h1 className="header-title">{title}</h1>
            {subtitle && <p className="header-subtitle">{subtitle}</p>}
          </div>
          {children && (
            <div className="header-actions">
              {children}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

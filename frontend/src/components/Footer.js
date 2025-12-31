import React from 'react';
import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="container">
        <div className="footer-content">
          <p className="footer-text">
            &copy; {currentYear} Weather Prediction System. All rights reserved.
          </p>
          <div className="footer-links">
            <a href="#about" className="footer-link">About</a>
            <a href="#privacy" className="footer-link">Privacy</a>
            <a href="#terms" className="footer-link">Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

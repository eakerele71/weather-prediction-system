import React from 'react';
import './DashboardContainer.css';

const DashboardContainer = ({ children }) => {
  return (
    <div className="dashboard-container">
      {children}
    </div>
  );
};

export default DashboardContainer;

import React from 'react';
import Chatbot from '@site/src/components/Chatbot';
import './ChatbotGlobal.css';

function Root({ children }) {
  return (
    <>
      {children}
      <div className="chatbot-float">
        <Chatbot />
      </div>
    </>
  );
}

export default Root;
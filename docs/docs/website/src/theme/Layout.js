import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import Chatbot from '@site/src/components/Chatbot';

function Layout(props) {
  const {children, ...layoutProps} = props;

  return (
    <>
      <OriginalLayout {...layoutProps}>{children}</OriginalLayout>
      <div className="chatbot-float">
        <Chatbot />
      </div>
    </>
  );
}

export default Layout;
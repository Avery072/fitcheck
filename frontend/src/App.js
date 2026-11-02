import React, { useState } from 'react';
import { Amplify } from 'aws-amplify';
import { awsConfig } from './config';
import Auth from './components/Auth';
import UploadPhoto from './components/UploadPhoto';
import VirtualTryOn from './components/VirtualTryOn';
import './App.css';

// Configure Amplify
Amplify.configure(awsConfig);

function App() {
  const [bodyAssetKey, setBodyAssetKey] = useState(null);

  return (
    <Auth>
      <div style={styles.container}>
        <UploadPhoto onUploadComplete={setBodyAssetKey} />
        <VirtualTryOn bodyAssetKey={bodyAssetKey} />
      </div>
    </Auth>
  );
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto'
  }
};

export default App;

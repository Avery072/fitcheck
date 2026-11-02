import React, { useState } from 'react';
import { uploadApi } from '../services/api';

const UploadPhoto = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);

    // Upload file
    setUploading(true);
    try {
      const extension = file.name.split('.').pop();
      const uploadData = await uploadApi.getUploadUrl('body', extension);

      await uploadApi.uploadFile(uploadData.url, file);

      onUploadComplete(uploadData.key);
      alert('Photo uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload photo. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Upload Your Photo</h2>
      <p style={styles.description}>
        Upload a full-body photo to try on clothes virtually
      </p>

      <div style={styles.uploadArea}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          disabled={uploading}
          style={styles.fileInput}
          id="photo-upload"
        />
        <label htmlFor="photo-upload" style={styles.uploadLabel}>
          {uploading ? 'Uploading...' : 'Choose Photo'}
        </label>
      </div>

      {preview && (
        <div style={styles.previewContainer}>
          <img src={preview} alt="Preview" style={styles.preview} />
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '30px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  title: {
    marginTop: 0,
    color: '#333',
    fontSize: '24px'
  },
  description: {
    color: '#666',
    marginBottom: '20px'
  },
  uploadArea: {
    marginBottom: '20px'
  },
  fileInput: {
    display: 'none'
  },
  uploadLabel: {
    display: 'inline-block',
    padding: '12px 24px',
    backgroundColor: '#4CAF50',
    color: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'background-color 0.3s'
  },
  previewContainer: {
    marginTop: '20px'
  },
  preview: {
    maxWidth: '300px',
    maxHeight: '400px',
    borderRadius: '8px',
    border: '2px solid #ddd'
  }
};

export default UploadPhoto;

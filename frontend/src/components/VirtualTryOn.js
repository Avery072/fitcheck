import React, { useState } from 'react';
import { multiFitApi } from '../services/api';
import { exampleItems, validCategories } from '../data/exampleItems';

const VirtualTryOn = ({ bodyAssetKey }) => {
  const [items, setItems] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [newItem, setNewItem] = useState({ imageUrl: '', title: '', category: 'shirt', retailer: '' });
  const [showExamples, setShowExamples] = useState(true);

  const addItem = () => {
    if (newItem.imageUrl && newItem.title) {
      setItems([...items, { ...newItem }]);
      setNewItem({ imageUrl: '', title: '', category: 'shirt', retailer: '' });
    }
  };

  const addExampleItem = (item) => {
    setItems([...items, { ...item }]);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const startTryOn = async () => {
    if (items.length === 0) {
      alert('Please add at least one clothing item');
      return;
    }

    setProcessing(true);
    try {
      const response = await multiFitApi.startTryOn(items, bodyAssetKey, sessionId);
      setSessionId(response.session_id);

      // Poll for status
      pollStatus(response.session_id);
    } catch (error) {
      console.error('Try-on failed:', error);
      alert('Failed to start virtual try-on. Please try again.');
      setProcessing(false);
    }
  };

  const pollStatus = async (sid) => {
    const poll = setInterval(async () => {
      try {
        const status = await multiFitApi.getStatus(sid);

        if (status.status === 'completed') {
          setResults(status);
          setProcessing(false);
          clearInterval(poll);
        } else if (status.status === 'failed') {
          alert('Virtual try-on failed. Please try again.');
          setProcessing(false);
          clearInterval(poll);
        }
      } catch (error) {
        console.error('Status check failed:', error);
        clearInterval(poll);
        setProcessing(false);
      }
    }, 3000); // Poll every 3 seconds

    // Stop polling after 5 minutes
    setTimeout(() => clearInterval(poll), 300000);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Virtual Try-On</h2>

      {!bodyAssetKey && (
        <div style={styles.warning}>
          Please upload your photo first!
        </div>
      )}

      {bodyAssetKey && (
        <>
          {showExamples && (
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Example Items</h3>
              <p style={styles.description}>Click to add example clothing items to try on:</p>
              <div style={styles.exampleGrid}>
                {exampleItems.map((item, index) => (
                  <div key={index} style={styles.exampleItem}>
                    <img src={item.imageUrl} alt={item.title} style={styles.exampleImage} />
                    <p style={styles.exampleTitle}>{item.title}</p>
                    <button onClick={() => addExampleItem(item)} style={styles.exampleButton}>
                      Add
                    </button>
                  </div>
                ))}
              </div>
              <button onClick={() => setShowExamples(false)} style={styles.hideButton}>
                Hide Examples
              </button>
            </div>
          )}

          {!showExamples && (
            <button onClick={() => setShowExamples(true)} style={styles.showButton}>
              Show Example Items
            </button>
          )}

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Add Custom Item</h3>
            <div style={styles.inputGroup}>
              <input
                type="text"
                placeholder="Clothing Title (e.g., Blue Denim Jacket)"
                value={newItem.title}
                onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                style={styles.input}
              />
              <input
                type="text"
                placeholder="Image URL"
                value={newItem.imageUrl}
                onChange={(e) => setNewItem({ ...newItem, imageUrl: e.target.value })}
                style={styles.input}
              />
              <select
                value={newItem.category}
                onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                style={styles.select}
              >
                {validCategories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Retailer (optional)"
                value={newItem.retailer}
                onChange={(e) => setNewItem({ ...newItem, retailer: e.target.value })}
                style={styles.input}
              />
              <button onClick={addItem} style={styles.addButton}>
                Add Custom Item
              </button>
            </div>
          </div>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Items to Try On ({items.length})</h3>
            {items.length === 0 ? (
              <p style={styles.emptyText}>No items added yet</p>
            ) : (
              <div style={styles.itemsList}>
                {items.map((item, index) => (
                  <div key={index} style={styles.item}>
                    <img src={item.imageUrl} alt={item.title} style={styles.itemImage} />
                    <div style={styles.itemInfo}>
                      <span style={styles.itemTitle}>{item.title}</span>
                      <button onClick={() => removeItem(index)} style={styles.removeButton}>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={startTryOn}
            disabled={processing || items.length === 0}
            style={{
              ...styles.tryOnButton,
              ...(processing || items.length === 0 ? styles.tryOnButtonDisabled : {})
            }}
          >
            {processing ? 'Processing...' : 'Start Virtual Try-On'}
          </button>

          {processing && (
            <div style={styles.processingInfo}>
              <div style={styles.spinner}></div>
              <p>Creating your virtual try-on... This may take a few moments.</p>
              {sessionId && <p style={styles.sessionId}>Session ID: {sessionId}</p>}
            </div>
          )}

          {results && (
            <div style={styles.results}>
              <h3 style={styles.resultsTitle}>Virtual Try-On Results</h3>
              <p style={styles.resultsSummary}>
                Completed {results.successful_items || 0} of {results.total_items || 0} items
              </p>
              <div style={styles.resultsGrid}>
                {results.results?.map((result, index) => (
                  <div key={index} style={styles.resultItem}>
                    <h4 style={styles.stepTitle}>
                      {result.item_index + 1}. {result.item_title}
                    </h4>
                    <img
                      src={result.image_url}
                      alt={`Try-on result ${index + 1}`}
                      style={styles.resultImage}
                    />
                    <p style={styles.resultMeta}>
                      {result.item_retailer && <span>Retailer: {result.item_retailer} | </span>}
                      Category: {result.item_category}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '30px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  title: {
    marginTop: 0,
    color: '#333',
    fontSize: '24px'
  },
  warning: {
    padding: '15px',
    backgroundColor: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '4px',
    color: '#856404'
  },
  section: {
    marginBottom: '30px'
  },
  sectionTitle: {
    color: '#333',
    fontSize: '18px',
    marginBottom: '15px'
  },
  inputGroup: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap'
  },
  input: {
    flex: 1,
    minWidth: '200px',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px'
  },
  addButton: {
    padding: '10px 20px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500'
  },
  emptyText: {
    color: '#999',
    fontStyle: 'italic'
  },
  itemsList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '15px'
  },
  item: {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '10px',
    backgroundColor: '#f9f9f9'
  },
  itemImage: {
    width: '100%',
    height: '150px',
    objectFit: 'cover',
    borderRadius: '4px',
    marginBottom: '10px'
  },
  itemInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  itemTitle: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333'
  },
  removeButton: {
    padding: '5px 10px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px'
  },
  tryOnButton: {
    width: '100%',
    padding: '15px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
    marginTop: '20px'
  },
  tryOnButtonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed'
  },
  processingInfo: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
    textAlign: 'center'
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #2196F3',
    borderRadius: '50%',
    width: '40px',
    height: '40px',
    animation: 'spin 1s linear infinite',
    margin: '0 auto'
  },
  sessionId: {
    fontSize: '12px',
    color: '#666',
    marginTop: '10px'
  },
  description: {
    color: '#666',
    marginBottom: '15px'
  },
  exampleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '15px'
  },
  exampleItem: {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '10px',
    textAlign: 'center',
    backgroundColor: '#fafafa'
  },
  exampleImage: {
    width: '100%',
    height: '120px',
    objectFit: 'cover',
    borderRadius: '4px',
    marginBottom: '8px'
  },
  exampleTitle: {
    fontSize: '12px',
    margin: '5px 0',
    color: '#333',
    height: '32px',
    overflow: 'hidden'
  },
  exampleButton: {
    padding: '6px 12px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    width: '100%'
  },
  hideButton: {
    padding: '8px 16px',
    backgroundColor: '#9E9E9E',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px'
  },
  showButton: {
    padding: '10px 20px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    marginBottom: '20px'
  },
  select: {
    flex: 1,
    minWidth: '150px',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    backgroundColor: 'white'
  },
  resultsSummary: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '15px'
  },
  resultMeta: {
    fontSize: '12px',
    color: '#666',
    marginTop: '8px'
  },
  results: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px'
  },
  resultsTitle: {
    marginTop: 0,
    color: '#333',
    marginBottom: '20px'
  },
  resultsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px'
  },
  resultItem: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  stepTitle: {
    marginTop: 0,
    marginBottom: '10px',
    color: '#333',
    fontSize: '16px'
  },
  resultImage: {
    width: '100%',
    height: 'auto',
    borderRadius: '4px'
  }
};

export default VirtualTryOn;

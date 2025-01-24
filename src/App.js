import React, { useState } from 'react';
import './App.css';

const constructionStocks = [

  { ticker: 'IBP', name: 'Installed Building Products, Inc.' },
  { ticker: 'SKY', name: 'Skyline Champion Corporation' },
  { ticker: 'KBH', name: 'KB Home' },
  { ticker: 'CVCO', name: 'Cavco Industries, Inc.' },
  { ticker: 'GRBK', name: 'Green Brick Partners, Inc.' },
  { ticker: 'TOL', name: 'Toll Brothers, Inc.' },
  { ticker: 'DHI', name: 'D.R. Horton, Inc.' },
  { ticker: 'LEN', name: 'Lennar Corporation' },
  { ticker: 'PHM', name: 'PulteGroup, Inc.' },
  { ticker: 'NVR', name: 'NVR, Inc.' }
];

function App() {
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockData, setStockData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStockData = async (ticker) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/stock-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.error) {
        console.error('Error in backend:', data.error);
      } else {
        setStockData(data);
      }
    } catch (error) {
      console.error('Error fetching stock data:', error);
    }
    setIsLoading(false);
  };

  const handleStockSelect = (stock) => {
    setSelectedStock(stock);
    fetchStockData(stock.ticker);
  };

  return (
    <div className="app">
      <h1>Construction Stock Analyzer</h1>

      <div className="stock-selector">
        <select 
          onChange={(e) => {
            const selected = constructionStocks.find(s => s.ticker === e.target.value);
            handleStockSelect(selected);
          }}
        >
          <option value="">Select a Stock</option>
          {constructionStocks.map((stock) => (
            <option key={stock.ticker} value={stock.ticker}>
              {stock.name} ({stock.ticker})
            </option>
          ))}
        </select>
      </div>

      {isLoading && <div className="loading">Loading...</div>}

      {selectedStock && stockData && (
        <div className="stock-details">
          <h2>{selectedStock.name} ({selectedStock.ticker})</h2>

          <div className="stock-info">
            <h3>Metrics:</h3>
            <ul>
              {Object.entries(stockData.metrics || {}).map(([key, value]) => (
                <li key={key}>{key}: {value}</li>
              ))}
            </ul>
          </div>

          <div className="ai-analysis">
            <h3>AI Analysis:</h3>
            <p>{stockData.aiAnalysis || 'No analysis available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

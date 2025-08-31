'use client';

import { useEffect } from 'react';
import { getFullApiUrl, testUrlGeneration, getConfigInfo } from '../../lib/config';

export default function DebugPage() {
  useEffect(() => {
    console.log('=== Debug Page Loaded ===');
    console.log('Config Info:', getConfigInfo());
    testUrlGeneration();
  }, []);

  const handleTestUrl = () => {
    const testPath = '/api/v1/analyze';
    const result = getFullApiUrl(testPath);
    console.log(`Manual test: "${testPath}" -> "${result}"`);
    alert(`URL Generated: ${result}`);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      <p className="mb-4">Check the browser console for configuration details.</p>
      <button 
        onClick={handleTestUrl}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Test URL Generation
      </button>
    </div>
  );
} 
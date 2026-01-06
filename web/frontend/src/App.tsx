import { useState } from 'react';
import { IntroductionPage } from './components/IntroductionPage';
import { CalculatorPage } from './components/CalculatorPage';

type Tab = 'introduction' | 'calculator';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('introduction');

  return (
    <div className="app">
      <header className="header">
        <h1>FIRE For Your Dynasty</h1>
        <p className="subtitle">
          Achieving generational wealth through compound interest
        </p>
        <nav className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'introduction' ? 'active' : ''}`}
            onClick={() => setActiveTab('introduction')}
          >
            Introduction
          </button>
          <button
            className={`tab-button ${activeTab === 'calculator' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculator')}
          >
            Calculator
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'introduction' ? (
          <IntroductionPage />
        ) : (
          <CalculatorPage />
        )}
      </main>

      <footer className="footer">
        <p>
          Based on the mathematical model: series converges when{' '}
          <code>k / (1+R)^Y_c &lt; 1</code>
        </p>
      </footer>
    </div>
  );
}

export default App;

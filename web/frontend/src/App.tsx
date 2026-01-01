import { useState } from 'react';
import { useCalculator } from './hooks/useCalculator';
import { ParameterSliders } from './components/ParameterSliders';
import { ResultsDisplay } from './components/ResultsDisplay';
import { ConvergenceHeatmap } from './components/ConvergenceHeatmap';
import { GenerationsTable } from './components/GenerationsTable';

function App() {
  const [currency, setCurrency] = useState('DKK');
  const {
    params,
    result,
    heatmapData,
    loading,
    error,
    updateParam,
    setParamsFromHeatmapClick,
  } = useCalculator();

  return (
    <div className="app">
      <header className="header">
        <h1>FIRE For Your Dynasty</h1>
        <p className="subtitle">
          Calculate how much to invest today for generational wealth
        </p>
      </header>

      <main className="main">
        <aside className="sidebar">
          <ParameterSliders
            params={params}
            currency={currency}
            onParamChange={updateParam}
            onCurrencyChange={setCurrency}
          />
        </aside>

        <section className="content">
          <div className="top-row">
            <div className="visualization">
              <ConvergenceHeatmap
                data={heatmapData}
                currentRoi={params.roi_rate}
                currentChildren={params.children_per_generation}
                onPointClick={setParamsFromHeatmapClick}
                loading={loading}
              />
            </div>

            <div className="generations-panel">
              <GenerationsTable
                convergence={result?.convergence ?? null}
                currency={currency}
                childrenPerGeneration={params.children_per_generation}
              />
            </div>
          </div>

          <div className="results-section">
            <ResultsDisplay
              result={result}
              loading={loading}
              error={error}
              currency={currency}
            />
          </div>
        </section>
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

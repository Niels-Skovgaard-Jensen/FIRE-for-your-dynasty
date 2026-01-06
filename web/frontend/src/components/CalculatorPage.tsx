import { useState } from 'react';
import { useCalculator } from '../hooks/useCalculator';
import { ParameterSliders } from './ParameterSliders';
import { ResultsDisplay } from './ResultsDisplay';
import { ConvergenceHeatmap } from './ConvergenceHeatmap';
import { GenerationsTable } from './GenerationsTable';

export function CalculatorPage() {
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
    <div className="calculator-page">
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
    </div>
  );
}

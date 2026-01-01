import type { CalculatorResult } from '../types/calculator';

interface Props {
  result: CalculatorResult | null;
  loading: boolean;
  error: string | null;
  currency: string;
}

function formatCurrency(amount: number, currency: string): string {
  const locales: Record<string, string> = {
    DKK: 'da-DK',
    USD: 'en-US',
    EUR: 'de-DE',
    GBP: 'en-GB',
    SEK: 'sv-SE',
    NOK: 'nb-NO',
  };
  return new Intl.NumberFormat(locales[currency] || 'en-US', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function ResultsDisplay({ result, loading, error, currency }: Props) {
  if (error) {
    return (
      <div className="results-container">
        <h2>Results</h2>
        <div className="results-grid">
          <div className="result-card error-card">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading && !result) {
    return (
      <div className="results-container">
        <h2>Results</h2>
        <div className="results-grid">
          <div className="result-card">
            <p>Calculating...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="results-container">
        <h2>Results</h2>
        <div className="results-grid">
          <div className="result-card">
            <p>Adjust parameters to see results</p>
          </div>
        </div>
      </div>
    );
  }

  const { convergence } = result;

  return (
    <div className="results-container">
      <h2>Results {loading && <span className="loading-indicator">...</span>}</h2>

      <div className="results-grid">
        <div className="result-card">
          <h3>Single Child Investment</h3>
          <p className="value">{formatCurrency(result.single_child_investment, currency)}</p>
          <p className="description">
            Amount needed today for one child to retire with target
          </p>
        </div>

        <div
          className={`result-card ${convergence.converges ? 'converges' : 'diverges'}`}
        >
          <h3>Convergence Status</h3>
          <p className="value status">
            {convergence.converges ? 'CONVERGES' : 'DIVERGES'}
          </p>
          <p className="detail">
            Ratio: {convergence.convergence_ratio.toFixed(4)}
            {convergence.convergence_ratio < 1 ? ' < 1' : ' >= 1'}
          </p>
        </div>

        {convergence.converges && convergence.infinite_sum && (
          <div className="result-card highlight">
            <h3>Infinite Dynasty Cost</h3>
            <p className="value">{formatCurrency(convergence.infinite_sum, currency)}</p>
            <p className="description">
              Total cost to fund infinite generations
            </p>
          </div>
        )}

        <div className="result-card">
          <h3>Max Children for Convergence</h3>
          <p className="value">{result.max_children_for_convergence.toFixed(2)}</p>
          <p className="description">
            Maximum children per generation at current ROI
          </p>
        </div>
      </div>
    </div>
  );
}

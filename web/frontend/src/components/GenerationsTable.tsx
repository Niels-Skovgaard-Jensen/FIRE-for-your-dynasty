import type { ConvergenceData } from '../types/calculator';

interface Props {
  convergence: ConvergenceData | null;
  currency: string;
  childrenPerGeneration: number;
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

export function GenerationsTable({ convergence, currency, childrenPerGeneration }: Props) {
  if (!convergence) {
    return (
      <div className="generations-table-container">
        <h2>Investment by Generation</h2>
        <p className="empty-state">No data available</p>
      </div>
    );
  }

  // Show first 10 generations (or fewer if not enough data)
  const maxRows = 10;
  const investments = convergence.investments.slice(0, maxRows);
  const cumulative = convergence.cumulative.slice(0, maxRows);

  return (
    <div className="generations-table-container">
      <h2>Investment by Generation</h2>
      <div className="table-wrapper">
        <table className="generations-table">
          <thead>
            <tr>
              <th>Gen</th>
              <th>People</th>
              <th>Investment</th>
              <th>Cumulative</th>
            </tr>
          </thead>
          <tbody>
            {investments.map((investment, index) => {
              // First generation has k children, each subsequent has k more
              const people = Math.pow(childrenPerGeneration, index + 1);
              return (
                <tr key={index}>
                  <td className="gen-number">{index + 1}</td>
                  <td className="people-count">
                    {people < 10 ? people.toFixed(1) : Math.round(people).toLocaleString()}
                  </td>
                  <td className="investment">{formatCurrency(investment, currency)}</td>
                  <td className="cumulative">{formatCurrency(cumulative[index], currency)}</td>
                </tr>
              );
            })}
          </tbody>
          {convergence.converges && convergence.infinite_sum && (
            <tfoot>
              <tr className="infinite-row">
                <td colSpan={2}>Infinite</td>
                <td>-</td>
                <td className="cumulative highlight">
                  {formatCurrency(convergence.infinite_sum, currency)}
                </td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}

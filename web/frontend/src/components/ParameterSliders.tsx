import type { CalculatorParams } from '../types/calculator';

const CURRENCIES = ['DKK', 'USD', 'EUR', 'GBP', 'SEK', 'NOK'] as const;

interface SliderConfig {
  key: keyof CalculatorParams;
  label: string;
  min: number;
  max: number;
  step: number;
  format: (v: number, currency?: string) => string;
  usesCurrency?: boolean;
}

const sliderConfigs: SliderConfig[] = [
  {
    key: 'target_amount',
    label: 'Target Amount',
    min: 100_000,
    max: 50_000_000,
    step: 100_000,
    format: (v, currency) => v >= 1_000_000
      ? `${(v / 1_000_000).toFixed(1)}M ${currency}`
      : `${(v / 1_000).toFixed(0)}K ${currency}`,
    usesCurrency: true,
  },
  {
    key: 'roi_rate',
    label: 'ROI Rate',
    min: 0.02,
    max: 0.15,
    step: 0.001,
    format: (v) => `${(v * 100).toFixed(1)}%`,
  },
  {
    key: 'retirement_age',
    label: 'Retirement Age',
    min: 0,
    max: 90,
    step: 1,
    format: (v) => `${v} years`,
  },
  {
    key: 'generation_gap',
    label: 'Generation Gap',
    min: 18,
    max: 40,
    step: 1,
    format: (v) => `${v} years`,
  },
  {
    key: 'children_per_generation',
    label: 'Children per Generation',
    min: 0.5,
    max: 6,
    step: 0.1,
    format: (v) => v.toFixed(1),
  },
];

interface Props {
  params: CalculatorParams;
  currency: string;
  onParamChange: <K extends keyof CalculatorParams>(
    key: K,
    value: CalculatorParams[K]
  ) => void;
  onCurrencyChange: (currency: string) => void;
}

export function ParameterSliders({ params, currency, onParamChange, onCurrencyChange }: Props) {
  return (
    <div className="parameter-sliders">
      <h2>Parameters</h2>

      <div className="currency-selector">
        <label htmlFor="currency">Currency</label>
        <select
          id="currency"
          value={currency}
          onChange={(e) => onCurrencyChange(e.target.value)}
        >
          {CURRENCIES.map((curr) => (
            <option key={curr} value={curr}>
              {curr}
            </option>
          ))}
        </select>
      </div>

      {sliderConfigs.map((config) => (
        <div key={config.key} className="slider-group">
          <div className="slider-header">
            <label htmlFor={config.key}>{config.label}</label>
            <span className="slider-value">
              {config.format(params[config.key] as number, config.usesCurrency ? currency : undefined)}
            </span>
          </div>
          <input
            id={config.key}
            type="range"
            min={config.min}
            max={config.max}
            step={config.step}
            value={params[config.key] as number}
            onChange={(e) =>
              onParamChange(config.key, parseFloat(e.target.value))
            }
          />
        </div>
      ))}
    </div>
  );
}

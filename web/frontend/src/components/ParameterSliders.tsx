import { useState } from 'react';
import type { CalculatorParams } from '../types/calculator';

const CURRENCIES = ['DKK', 'USD', 'EUR', 'GBP', 'SEK', 'NOK'] as const;

interface SliderConfig {
  key: keyof CalculatorParams;
  label: string;
  min: number;
  max: number;
  step: number;
  format: (v: number, currency?: string) => string;
  parseInput: (v: string) => number;
  inputType: 'currency' | 'percent' | 'number';
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
    parseInput: (v) => parseFloat(v) || 0,
    inputType: 'currency',
    usesCurrency: true,
  },
  {
    key: 'roi_rate',
    label: 'ROI Rate',
    min: 0.02,
    max: 0.15,
    step: 0.001,
    format: (v) => `${(v * 100).toFixed(1)}%`,
    parseInput: (v) => (parseFloat(v) || 0) / 100,
    inputType: 'percent',
  },
  {
    key: 'retirement_age',
    label: 'Retirement Age',
    min: 0,
    max: 90,
    step: 1,
    format: (v) => `${v} years`,
    parseInput: (v) => parseInt(v) || 0,
    inputType: 'number',
  },
  {
    key: 'generation_gap',
    label: 'Generation Gap',
    min: 18,
    max: 40,
    step: 1,
    format: (v) => `${v} years`,
    parseInput: (v) => parseInt(v) || 0,
    inputType: 'number',
  },
  {
    key: 'children_per_generation',
    label: 'Children per Generation',
    min: 0.5,
    max: 6,
    step: 0.1,
    format: (v) => v.toFixed(1),
    parseInput: (v) => parseFloat(v) || 0,
    inputType: 'number',
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

function getInputValue(config: SliderConfig, value: number): string {
  switch (config.inputType) {
    case 'currency':
      return value.toString();
    case 'percent':
      return (value * 100).toFixed(1);
    case 'number':
      return config.step < 1 ? value.toFixed(1) : value.toString();
  }
}

function getInputSuffix(config: SliderConfig, currency?: string): string {
  switch (config.inputType) {
    case 'currency':
      return currency || '';
    case 'percent':
      return '%';
    case 'number':
      return config.key === 'retirement_age' || config.key === 'generation_gap' ? 'yrs' : '';
  }
}

export function ParameterSliders({ params, currency, onParamChange, onCurrencyChange }: Props) {
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState<string>('');

  const handleInputStart = (config: SliderConfig, value: number) => {
    setEditingKey(config.key);
    setInputValue(getInputValue(config, value));
  };

  const handleInputEnd = (config: SliderConfig) => {
    const parsed = config.parseInput(inputValue);
    onParamChange(config.key, parsed);
    setEditingKey(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent, config: SliderConfig) => {
    if (e.key === 'Enter') {
      handleInputEnd(config);
    } else if (e.key === 'Escape') {
      setEditingKey(null);
    }
  };

  return (
    <div className="parameter-sliders">
      <h2>Parameters</h2>
      <p className="parameters-hint">Click on values to edit manually</p>

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
            {editingKey === config.key ? (
              <div className="slider-input-wrapper">
                <input
                  type="text"
                  className="slider-input"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onBlur={() => handleInputEnd(config)}
                  onKeyDown={(e) => handleKeyDown(e, config)}
                  autoFocus
                />
                <span className="slider-input-suffix">
                  {getInputSuffix(config, config.usesCurrency ? currency : undefined)}
                </span>
              </div>
            ) : (
              <span
                className="slider-value"
                onClick={() => handleInputStart(config, params[config.key] as number)}
                title="Click to edit"
              >
                {config.format(params[config.key] as number, config.usesCurrency ? currency : undefined)}
              </span>
            )}
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

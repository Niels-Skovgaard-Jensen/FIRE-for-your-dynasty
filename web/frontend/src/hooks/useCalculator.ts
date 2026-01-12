import { useState, useEffect, useCallback, useMemo } from 'react';
import { debounce } from 'lodash-es';
import { calculateDynasty, generateHeatmapData } from '../services/calculator';
import type {
  CalculatorParams,
  CalculatorResult,
  HeatmapData,
} from '../types/calculator';

const DEFAULT_PARAMS: CalculatorParams = {
  target_amount: 2_000_000,
  roi_rate: 0.07,
  retirement_age: 65,
  generation_gap: 30,
  children_per_generation: 2.0,
  max_generations: 20,
};

export function useCalculator(initialParams: Partial<CalculatorParams> = {}) {
  const [params, setParams] = useState<CalculatorParams>({
    ...DEFAULT_PARAMS,
    ...initialParams,
  });
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debounced calculation (100ms delay - faster now since it's local)
  const debouncedCalculate = useMemo(
    () =>
      debounce((p: CalculatorParams) => {
        setLoading(true);
        setError(null);
        try {
          const calcResult = calculateDynasty(p);
          const heatmap = generateHeatmapData({
            target_amount: p.target_amount,
            retirement_age: p.retirement_age,
            generation_gap: p.generation_gap,
            roi_range: [0.02, 0.15],
            children_range: [0.5, 6],
            resolution: 80,
          });
          setResult(calcResult);
          setHeatmapData(heatmap);
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Calculation failed');
        } finally {
          setLoading(false);
        }
      }, 100),
    []
  );

  useEffect(() => {
    debouncedCalculate(params);
    return () => debouncedCalculate.cancel();
  }, [params, debouncedCalculate]);

  const updateParam = useCallback(
    <K extends keyof CalculatorParams>(key: K, value: CalculatorParams[K]) => {
      setParams((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const setParamsFromHeatmapClick = useCallback(
    (roi: number, children: number) => {
      setParams((prev) => ({
        ...prev,
        roi_rate: roi,
        children_per_generation: children,
      }));
    },
    []
  );

  return {
    params,
    result,
    heatmapData,
    loading,
    error,
    updateParam,
    setParamsFromHeatmapClick,
  };
}

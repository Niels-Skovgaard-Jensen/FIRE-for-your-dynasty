export interface CalculatorParams {
  target_amount: number;
  roi_rate: number;
  retirement_age: number;
  generation_gap: number;
  children_per_generation: number;
  max_generations?: number;
}

export interface ConvergenceData {
  converges: boolean;
  convergence_ratio: number;
  infinite_sum: number | null;
  investments: number[];
  cumulative: number[];
}

export interface CalculatorResult {
  single_child_investment: number;
  convergence: ConvergenceData;
  max_children_for_convergence: number;
}

export interface HeatmapParams {
  target_amount: number;
  retirement_age: number;
  generation_gap: number;
  roi_range: [number, number];
  children_range: [number, number];
  resolution: number;
}

export interface HeatmapData {
  roi_values: number[];
  children_values: number[];
  convergence_matrix: number[][];
  convergence_ratios: number[][];
  infinite_sums: (number | null)[][];
}

/**
 * Client-side Dynasty FIRE calculator
 * Replicates the Python DynastyFIRE calculation logic
 */

import type {
  CalculatorParams,
  CalculatorResult,
  ConvergenceData,
  HeatmapParams,
  HeatmapData,
} from '../types/calculator';

/**
 * Calculate initial investment needed for one child's retirement
 * Formula: B = M / (1 + R)^Y
 */
function calculateSingleChildInvestment(
  targetAmount: number,
  roiRate: number,
  retirementAge: number
): number {
  return targetAmount / Math.pow(1 + roiRate, retirementAge);
}

/**
 * Calculate maximum children per generation that still converges
 */
function calculateMaxChildrenForConvergence(
  roiRate: number,
  generationGap: number
): number {
  return Math.pow(1 + roiRate, generationGap);
}

/**
 * Analyze convergence of infinite dynasty investment series
 * The infinite series converges when: k / (1+R)^Y_c < 1
 */
function convergenceAnalysis(
  targetAmount: number,
  roiRate: number,
  retirementAge: number,
  generationGap: number,
  childrenPerGeneration: number,
  maxGenerations: number = 20
): ConvergenceData {
  // Calculate convergence ratio
  const convergenceRatio =
    childrenPerGeneration / Math.pow(1 + roiRate, generationGap);
  let converges = convergenceRatio < 1;

  const investments: number[] = [];
  const cumulative: number[] = [];
  let runningTotal = 0;

  // Simulate finite generations with overflow protection
  for (let n = 0; n < maxGenerations; n++) {
    const years = retirementAge + n * generationGap;

    try {
      // First generation has k children, each subsequent has k more
      const term = Math.pow(childrenPerGeneration, n + 1);
      const discount = Math.pow(1 + roiRate, years);

      // Prevent overflow by checking if numbers are getting too large
      if (term > 1e100 || discount > 1e100) {
        break;
      }

      const investment = (targetAmount * term) / discount;

      // Additional check for extremely large values
      if (investment > 1e50 || !Number.isFinite(investment)) {
        break;
      }

      investments.push(investment);
      runningTotal += investment;
      cumulative.push(runningTotal);
    } catch {
      // Handle overflow - series is diverging
      break;
    }
  }

  // Calculate theoretical infinite sum if convergent
  let infiniteSum: number | null = null;
  if (converges) {
    try {
      // Sum = a / (1 - r) where a = first term, r = common ratio
      // First generation has k children, so first term is k * M / (1+R)^Y
      const a =
        (childrenPerGeneration * targetAmount) /
        Math.pow(1 + roiRate, retirementAge);
      const r = childrenPerGeneration / Math.pow(1 + roiRate, generationGap);

      // Additional check: if r is very close to 1, the sum may be unstable
      if (Math.abs(1 - r) < 1e-10) {
        infiniteSum = null;
        converges = false;
      } else {
        infiniteSum = a / (1 - r);
        if (!Number.isFinite(infiniteSum)) {
          infiniteSum = null;
          converges = false;
        }
      }
    } catch {
      infiniteSum = null;
      converges = false;
    }
  }

  return {
    converges,
    convergence_ratio: convergenceRatio,
    investments,
    cumulative,
    infinite_sum: infiniteSum,
  };
}

/**
 * Main calculation function - replaces API call
 */
export function calculateDynasty(params: CalculatorParams): CalculatorResult {
  const {
    target_amount,
    roi_rate,
    retirement_age,
    generation_gap,
    children_per_generation,
    max_generations = 20,
  } = params;

  const singleChildInvestment = calculateSingleChildInvestment(
    target_amount,
    roi_rate,
    retirement_age
  );

  const convergence = convergenceAnalysis(
    target_amount,
    roi_rate,
    retirement_age,
    generation_gap,
    children_per_generation,
    max_generations
  );

  const maxChildrenForConvergence = calculateMaxChildrenForConvergence(
    roi_rate,
    generation_gap
  );

  return {
    single_child_investment: singleChildInvestment,
    convergence,
    max_children_for_convergence: maxChildrenForConvergence,
  };
}

/**
 * Generate heatmap data - replaces API call
 */
export function generateHeatmapData(params: HeatmapParams): HeatmapData {
  const {
    target_amount,
    retirement_age,
    generation_gap,
    roi_range,
    children_range,
    resolution,
  } = params;

  // Generate axis values
  const roiValues: number[] = [];
  const roiStep = (roi_range[1] - roi_range[0]) / (resolution - 1);
  for (let i = 0; i < resolution; i++) {
    roiValues.push(roi_range[0] + i * roiStep);
  }

  const childrenValues: number[] = [];
  const childrenStep =
    (children_range[1] - children_range[0]) / (resolution - 1);
  for (let i = 0; i < resolution; i++) {
    childrenValues.push(children_range[0] + i * childrenStep);
  }

  // Generate matrices
  const convergenceMatrix: number[][] = [];
  const convergenceRatios: number[][] = [];
  const infiniteSums: (number | null)[][] = [];

  for (let i = 0; i < childrenValues.length; i++) {
    const children = childrenValues[i];
    const convergenceRow: number[] = [];
    const ratioRow: number[] = [];
    const sumRow: (number | null)[] = [];

    for (let j = 0; j < roiValues.length; j++) {
      const roi = roiValues[j];

      const analysis = convergenceAnalysis(
        target_amount,
        roi,
        retirement_age,
        generation_gap,
        children,
        20
      );

      convergenceRow.push(analysis.converges ? 1 : 0);
      ratioRow.push(analysis.convergence_ratio);
      sumRow.push(analysis.infinite_sum);
    }

    convergenceMatrix.push(convergenceRow);
    convergenceRatios.push(ratioRow);
    infiniteSums.push(sumRow);
  }

  return {
    roi_values: roiValues,
    children_values: childrenValues,
    convergence_matrix: convergenceMatrix,
    convergence_ratios: convergenceRatios,
    infinite_sums: infiniteSums,
  };
}

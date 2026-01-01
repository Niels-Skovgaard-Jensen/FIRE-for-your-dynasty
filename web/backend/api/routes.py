"""API routes for Dynasty FIRE calculations"""

from flask import Blueprint, request, jsonify

from ..services.calculator_service import CalculatorService

api_bp = Blueprint("api", __name__)


@api_bp.route("/calculate", methods=["POST"])
def calculate():
    """Main calculation endpoint

    Request body:
        target_amount: float (default: 10_000_000)
        roi_rate: float (default: 0.07)
        retirement_age: float (default: 72)
        generation_gap: float (default: 25)
        children_per_generation: float (default: 2.0)
        max_generations: int (default: 20)

    Returns:
        single_child_investment: float
        convergence: dict with converges, convergence_ratio, infinite_sum
        max_children_for_convergence: float
    """
    params = request.get_json() or {}
    try:
        result = CalculatorService.calculate(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/heatmap", methods=["POST"])
def heatmap():
    """Generate heatmap data for visualization

    Request body:
        target_amount: float
        retirement_age: float
        generation_gap: float
        roi_range: [float, float] (default: [0.03, 0.12])
        children_range: [float, float] (default: [1, 5])
        resolution: int (default: 50)

    Returns:
        roi_values: list of floats
        children_values: list of floats
        convergence_matrix: 2D array of 0/1
        convergence_ratios: 2D array of floats
        infinite_sums: 2D array of floats or nulls
    """
    params = request.get_json() or {}
    try:
        result = CalculatorService.generate_heatmap_data(params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "dynasty-fire-api"})

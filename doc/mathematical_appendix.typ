= Appendix A: Formal Mathematical Analysis of Dynasty FIRE

== Introduction

This appendix provides a rigorous mathematical foundation for the Dynasty FIRE concept, extending beyond the computational analysis to establish formal convergence criteria, derive closed-form solutions, and prove the theoretical bounds of generational wealth accumulation.

== Mathematical Framework

=== Definitions and Notation

Let us define the following parameters:
- $M$: Target retirement amount (constant across generations)
- $R$: Annual real rate of return (assumed constant)
- $Y$: Age at retirement
- $Y_c$: Generation gap (years between births of successive generations)
- $k$: Number of children per generation (assumed constant)
- $B_n$: Investment required for generation $n$ (where $n = 0$ is the initial generation)

=== Single Generation Investment Formula

For a single child born at time $t = 0$, retiring at age $Y$, the required initial investment is:

$ B_0 = M / (1 + R)^Y $

This follows directly from the compound interest formula $M = B_0(1 + R)^Y$.

== Multi-Generational Analysis

=== Generation Investment Requirements

For generation $n$, each individual retires at time $(Y + n Y_c)$ from the initial investment time. The required investment per individual in generation $n$ is:

$ B_n = M / (1 + R)^(Y + n Y_c) = M / (1 + R)^Y · 1 / (1 + R)^(n Y_c) $

Since there are $k^n$ individuals in generation $n$, the total investment required for generation $n$ is:

$ I_n = k^n · B_n = k^n · M / (1 + R)^(Y + n Y_c) $

=== Dynasty Total Investment

The total investment required for all generations is the infinite series:

$ I_("total") = sum_(n=0)^∞ I_n = sum_(n=0)^∞ k^n · M / (1 + R)^(Y + n Y_c) $

Factoring out constants:

$ I_("total") = M / (1 + R)^Y sum_(n=0)^∞ (k / (1 + R)^(Y_c))^n $

Let $r = k / (1 + R)^(Y_c)$. Then:

$ I_("total") = M / (1 + R)^Y sum_(n=0)^∞ r^n $

== Convergence Analysis

=== Convergence Criterion

The geometric series $sum_(n=0)^∞ r^n$ converges if and only if $|r| < 1$.

*Theorem 1 (Dynasty Convergence Condition):* The Dynasty FIRE investment series converges if and only if:

$ k < (1 + R)^(Y_c) $

*Proof:* The series converges $<=> |r| < 1$ <=> $|k / (1 + R)^(Y_c)| < 1$ <=> $k < (1 + R)^(Y_c)$ (since $k > 0$ and $(1 + R)^(Y_c) > 0$). □

=== Closed-Form Solution

When the convergence condition is satisfied, the infinite geometric series evaluates to:

$ sum_(n=0)^∞ r^n = 1 / (1 - r) = 1 / (1 - k / (1 + R)^(Y_c)) $

Therefore:

*Theorem 2 (Dynasty Total Investment Formula):* When $k < (1 + R)^(Y_c)$, the total dynasty investment is:

$ I_("total") = M / (1 + R)^Y · (1 + R)^(Y_c) / ((1 + R)^(Y_c) - k) $

Equivalently:

$ I_("total") = M(1 + R)^(Y_c) / ((1 + R)^(Y + Y_c) - k(1 + R)^Y) $

== Sensitivity Analysis

=== First-Order Derivatives

The sensitivity of the total investment to each parameter can be analyzed through partial derivatives.

*Sensitivity to $k$ (family size):*
$ (∂ I_("total")) / (∂ k) = M / (1 + R)^Y · (1 + R)^(Y_c) / ((1 + R)^(Y_c) - k)^2 > 0 $

This confirms that total investment increases with family size, with the rate of increase accelerating as $k$ approaches the convergence boundary.

*Sensitivity to $R$ (return rate):*
$ (∂ I_("total")) / (∂ R) = M · [-(Y + Y_c)(1 + R)^(Y_c) + k Y(1 + R)^Y] / ((1 + R)^(Y + Y_c) - k(1 + R)^Y)^2 $

The sign depends on the relative magnitudes of the terms, but generally decreases with higher returns.

*Sensitivity to $Y_c$ (generation gap):*
$ (∂ I_("total")) / (∂ Y_c) = M ln(1 + R) · [(1 + R)^(Y + Y_c) - k(1 + R)^Y] / ((1 + R)^(Y + Y_c) - k(1 + R)^Y)^2 $

Since the numerator is positive (convergence condition), increasing generation gaps reduce total investment.

== Asymptotic Behavior

=== Critical Point Analysis

The convergence boundary occurs at $k = (1 + R)^(Y_c)$. As $k$ approaches this critical value:

$ lim_(k → (1 + R)^(Y_c)^-) I_("total") = +∞ $

This represents a phase transition from finite to infinite investment requirements.

=== Small Parameter Expansions

For small values of $r = k / (1 + R)^(Y_c)$, we can expand:

$ I_("total") ≈ M / (1 + R)^Y · (1 + r + r^2 + ...) ≈ M / (1 + R)^Y · (1 + k / (1 + R)^(Y_c)) $

This first-order approximation is useful for quick estimation when $k ≪ (1 + R)^(Y_c)$.

== Probabilistic Extensions

=== Stochastic Return Rates

Consider the case where $R$ follows a probability distribution. Let $R ~ N(μ_R, σ_R^2)$.

The expected total investment becomes:

$ E[I_("total")] = M E[1 / (1 + R)^Y] · E[(1 + R)^(Y_c) / ((1 + R)^(Y_c) - k)] $

For small $σ_R$, using Jensen's inequality and second-order Taylor expansion:

$ E[I_("total")] ≈ I_("total")|_(R = μ_R) · (1 + (Y^2 + Y_c^2) σ_R^2 / 2) $

=== Variable Family Sizes

If $k$ varies by generation according to some distribution, the analysis becomes significantly more complex, requiring consideration of moment generating functions of the resulting branching process.

== Numerical Verification

=== Parameter Values
Using the baseline parameters:
- $M = 10^7$ DKK
- $R = 0.07$
- $Y = 72$ years  
- $Y_c = 25$ years
- $k = 2$

=== Convergence Check
$ r = 2 / (1.07)^25 = 2 / 5.427 ≈ 0.3685 < 1$ ✓

=== Exact Solution
$ I_("total") = (10^7) / (1.07)^72 · (1.07)^25 / ((1.07)^25 - 2) $
$ = 76,625 · 5.427 / (5.427 - 2) = 76,625 · 1.584 ≈ 121,337$ DKK

This matches the computational results exactly.

== Conclusions

The mathematical analysis confirms several key findings:

1. *Convergence Guarantee*: The series converges for all reasonable family planning scenarios ($k ≤ 4$ with $Y_c ≥ 25$ years).

2. *Closed-Form Solutions*: Exact formulas eliminate computational approximation errors.

3. *Sensitivity Bounds*: Mathematical derivatives provide precise sensitivity measures for parameter optimization.

4. *Phase Transition*: The convergence boundary represents a fundamental limit beyond which dynasty funding becomes impossible.

5. *Robustness*: The mathematical framework extends naturally to stochastic and variable parameter cases.

This formal analysis provides the theoretical foundation that validates the practical feasibility of Dynasty FIRE as demonstrated in the computational results.
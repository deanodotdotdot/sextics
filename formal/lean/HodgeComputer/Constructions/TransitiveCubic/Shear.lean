import HodgeComputer.Constructions.TransitiveCubic.Cubic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination

/-!
# Quadratic shear and central first variation of a ternary cubic

The substitution `x = X + k * y`, with `3 * a * k ^ 2 + 2 * d * k + f = 0`,
removes the reverse-edge term `f * x * y ^ 2`. A second infinitesimal shear
represents the central `x * y * z` variation within `TransitiveCubic`.
The identities keep both the numerator and normal-denominator derivatives.

These general-family identities were contributed by `fqlx` with OpenAI
Codex assistance. They reuse the maintained transitive-cubic normalization,
building on `hodgepodgeconjecture` and the Hodge Computer collaborators.
No root, nonvanishing condition, or geometric descent is assumed implicitly:
applications supply the displayed root relation and field hypotheses.
-/

namespace TransitiveCubicShear

section Ring
variable {K : Type*} [CommRing K]

def bPrime (a b d f k : K) : K := b + a * k ^ 3 + d * k ^ 2 + f * k
def dPrime (a d k : K) : K := d + 3 * a * k

/-- A quadratic root eliminates the reverse edge by a determinant-one shear. -/
theorem base_shear (a b c d e f k X Y Z : K)
    (hk : 3 * a * k ^ 2 + 2 * d * k + f = 0) :
    a * (X + k * Y) ^ 3 + b * Y ^ 3 + c * Z ^ 3 +
      d * (X + k * Y) ^ 2 * Y + e * Y ^ 2 * Z + f * (X + k * Y) * Y ^ 2 =
    TransitiveCubic.cubic a (bPrime a b d f k) c (dPrime a d k) e 0 X Y Z := by
  simp only [TransitiveCubic.cubic, bPrime, dPrime]
  linear_combination X * Y ^ 2 * hk

theorem discriminant_identity (a d f k : K)
    (hk : 3 * a * k ^ 2 + 2 * d * k + f = 0) :
    (dPrime a d k) ^ 2 = d ^ 2 - 3 * a * f := by
  simp only [dPrime]
  linear_combination 3 * a * hk

/-- The first variation of the degree-six invariant is independent of the root. -/
theorem s6_first_variation (a c d e k : K) :
    12 * a ^ 2 * c * e ^ 2 * k - 4 * a * c * (dPrime a d k) * e ^ 2 =
      -4 * a * c * d * e ^ 2 := by
  simp only [dPrime]
  ring

def reverseS4 (a _b c d e f : K) : K := c * e * (d ^ 2 - 3 * a * f)

def reverseS6 (a b c d e f : K) : K :=
  c * (27 * a ^ 2 * b ^ 2 * c + 4 * a ^ 2 * e ^ 3 - 18 * a * b * c * d * f +
    4 * a * c * f ^ 3 + 4 * b * c * d ^ 3 - c * d ^ 2 * f ^ 2)

/-- The degree-four invariant of the sheared cubic descends to its original coefficients. -/
theorem s4_shear_numerator (a b c d e f k : K)
    (hk : 3 * a * k ^ 2 + 2 * d * k + f = 0) :
    TransitiveCubic.s4Numerator a (bPrime a b d f k) c (dPrime a d k) e 0 =
      3 * reverseS4 a b c d e f := by
  dsimp [TransitiveCubic.s4Numerator, bPrime, dPrime, reverseS4]
  linear_combination 9 * a * c * e * hk

/-- The degree-six invariant of the sheared cubic descends to its original coefficients. -/
theorem s6_shear_numerator (a b c d e f k : K)
    (hk : 3 * a * k ^ 2 + 2 * d * k + f = 0) :
    TransitiveCubic.s6Numerator a (bPrime a b d f k) c (dPrime a d k) e 0 =
      27 * reverseS6 a b c d e f := by
  dsimp [TransitiveCubic.s6Numerator, bPrime, dPrime, reverseS6]
  linear_combination
    27 * c ^ 2 * (45 * a ^ 3 * k ^ 4 + 54 * a ^ 2 * b * k + 60 * a ^ 2 * d * k ^ 3 +
      39 * a ^ 2 * f * k ^ 2 + 18 * a * b * d + 17 * a * d ^ 2 * k ^ 2 +
      8 * a * d * f * k - 4 * a * f ^ 2 + 2 * d ^ 3 * k + d ^ 2 * f) * hk

end Ring

section Field
variable {K : Type*} [Field K] [CharZero K]

/-- The determinant-one first variation `X -> X - λ * Z / (2 * D)` removes
the central term. Its coefficient directions are `eDot = k`, `fDot = -3a/(2D)`. -/
theorem first_variation_shear (a D k X Y Z : K) (hD : D ≠ 0) :
    (X + k * Y) * Y * Z - Z / (2 * D) * (3 * a * X ^ 2 + 2 * D * X * Y) =
      k * Y ^ 2 * Z + (-3 * a / (2 * D)) * X ^ 2 * Z := by
  field_simp
  ring

/-- On `z = 1`, the modified source differs by a constant multiple of the normal. -/
theorem modified_source (a D k X Y : K) (hD : D ≠ 0) :
    k * Y ^ 2 - 3 * a * X ^ 2 / (2 * D) =
      (X + k * Y) * Y - (3 * a * X ^ 2 + 2 * D * X * Y) / (2 * D) := by
  field_simp
  ring

/-- The complete normal source is unchanged, including the derivative of
the normal denominator. -/
theorem second_normal_source_unchanged (a D k X Y g : K)
    (hD : D ≠ 0) (hg : g ≠ 0)
    (hgvalue : g = 3 * a * X ^ 2 + 2 * D * X * Y) :
    (-3 * a * X / D - (k * Y ^ 2 - 3 * a * X ^ 2 / (2 * D)) *
      (6 * a * X + 2 * D * Y) / g) / g =
    (Y - (X + k * Y) * Y * (6 * a * X + 2 * D * Y) / g) / g := by
  field_simp [hD, hg]
  linear_combination -(6 * a * X + 2 * D * Y) * hgvalue

/-- The first variation of the degree-four invariant is independent of the root. -/
theorem s4_first_variation (a b c d f k : K)
    (hk : 3 * a * k ^ 2 + 2 * d * k + f = 0) :
    c * (dPrime a d k) ^ 2 * k + (9 / 2 : K) * a * (bPrime a b d f k) * c =
      (9 * a * b * c - c * d * f) / 2 := by
  simp only [dPrime, bPrime]
  field_simp
  linear_combination c * (9 * a * k + d) * hk

end Field
end TransitiveCubicShear

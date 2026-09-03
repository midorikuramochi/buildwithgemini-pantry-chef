"""Tool for scaling recipe ingredient quantities and cooking times for different serving sizes."""

import math
import re
from fractions import Fraction
from typing import Any


def _parse_and_scale_quantity(quantity_str: str, factor: float) -> str:
    """Parse a numerical quantity (int, float, fraction) and scale it."""
    quantity_str = quantity_str.strip()
    try:
        # Check for mixed fractions like "1 1/2"
        if " " in quantity_str:
            parts = quantity_str.split()
            val = float(parts[0]) + float(Fraction(parts[1]))
        elif "/" in quantity_str:
            val = float(Fraction(quantity_str))
        else:
            val = float(quantity_str)

        scaled = val * factor

        # Clean integer display
        if scaled.is_integer():
            return str(int(scaled))
        if abs(scaled - round(scaled)) < 0.02:
            return str(round(scaled))

        # Check for common culinary fractions
        for frac, frac_str in [
            (0.5, "1/2"),
            (0.25, "1/4"),
            (0.75, "3/4"),
            (0.33, "1/3"),
            (0.67, "2/3"),
            (0.125, "1/8"),
        ]:
            whole = math.floor(scaled)
            remainder = scaled - whole
            if abs(remainder - frac) < 0.04:
                return f"{whole} {frac_str}".strip() if whole > 0 else frac_str

        return f"{scaled:.2f}".rstrip("0").rstrip(".")
    except Exception:
        return quantity_str


def scale_recipe_servings(
    ingredients: list[str],
    original_servings: int,
    target_servings: int,
    cook_time_minutes: int | None = None,
) -> dict[str, Any]:
    """Scales ingredient quantities and adjusts cook time for a different number of servings.

    Args:
        ingredients: List of ingredients with quantities (e.g. ["1 lb chicken breast", "2 cups broccoli florets", "2 tbsp soy sauce"]).
        original_servings: Original recipe yield in servings (e.g. 2).
        target_servings: Desired number of servings (e.g. 4).
        cook_time_minutes: Optional cook time in minutes to estimate time adjustment.

    Returns:
        Dictionary with scaled ingredients, scaling factor, and estimated cook time.
    """
    if original_servings <= 0:
        return {"error": "original_servings must be greater than 0"}
    if target_servings <= 0:
        return {"error": "target_servings must be greater than 0"}

    factor = target_servings / original_servings
    scaled_ingredients: list[str] = []

    # Regex matches leading numbers, fractions (e.g., "1 1/2", "1/2", "2.5", "2")
    num_pattern = re.compile(r"^(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)\s*(.*)$")

    for item in ingredients:
        match = num_pattern.match(item.strip())
        if match:
            num_part = match.group(1)
            rest_part = match.group(2)
            scaled_num = _parse_and_scale_quantity(num_part, factor)
            scaled_ingredients.append(f"{scaled_num} {rest_part}".strip())
        else:
            scaled_ingredients.append(item)

    adjusted_cook_time = None
    cook_time_note = "Cook time remains unchanged."
    if cook_time_minutes is not None and cook_time_minutes > 0:
        if factor > 1.0:
            time_factor = 1.0 + 0.15 * math.log2(factor)
            adjusted_cook_time = round(cook_time_minutes * time_factor)
            cook_time_note = (
                f"Slightly increased from {cook_time_minutes}m to {adjusted_cook_time}m "
                f"due to larger batch size."
            )
        elif factor < 1.0:
            time_factor = max(0.75, 1.0 - 0.15 * math.log2(1.0 / factor))
            adjusted_cook_time = round(cook_time_minutes * time_factor)
            cook_time_note = (
                f"Reduced from {cook_time_minutes}m to {adjusted_cook_time}m "
                f"for smaller portion size."
            )
        else:
            adjusted_cook_time = cook_time_minutes

    return {
        "original_servings": original_servings,
        "target_servings": target_servings,
        "scale_factor": round(factor, 2),
        "scaled_ingredients": scaled_ingredients,
        "original_cook_time_minutes": cook_time_minutes,
        "adjusted_cook_time_minutes": adjusted_cook_time,
        "cook_time_note": cook_time_note,
    }

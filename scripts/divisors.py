"""Validate compact, exact polynomial formulas used only for surface shading."""

from fractions import Fraction
import math


def validate_slice_identity(data, denominator, render, folder):
    """Check a factored formula or lower-multiplicity display exactly on B's slice."""
    import sympy as sp

    def require(ok, message):
        if not ok:
            raise ValueError(f"{folder.name}: divisor slice identity: {message}")

    require(data.get("kind") == "polynomial-program", "expected a polynomial program")
    power = data.get("sliceIdentity", {}).get("power")
    require(type(power) is int and 1 <= power <= 8, "invalid power")
    require(data["degree"] * power == denominator["degree"] <= 64, "unsupported degree")
    variables = sp.symbols("X0 X1 X2 Y0 Y1 Y2")
    nodes = []
    for op, *args in data["nodes"]:
        if op == "variable":
            value = variables[args[0]]
        elif op == "rational":
            value = sp.Rational(args[0])
        elif op == "sqrt":
            value = sp.sqrt(args[0])
        elif op == "add":
            value = nodes[args[0]] + nodes[args[1]]
        elif op == "mul":
            value = nodes[args[0]] * nodes[args[1]]
        elif op == "pow":
            value = nodes[args[0]] ** args[1]
        nodes.append(value)
    displayed = nodes[data["output"]]
    original = sum(
        sp.Rational(c) * sp.prod(x**e for x, e in zip(variables, exponents))
        for c, exponents in denominator["terms"]
    )
    u = sp.symbols("u0:4")
    # Interpret the stored decimal coefficients exactly; no tolerance can turn
    # a merely nearby curve into an authorized replacement for D = 0.
    coordinates = [
        (sp.I if sign < 0 else 1) * sum(sp.Rational(str(b)) * v for b, v in zip(row, u))
        for row, sign in zip(render["planeMatrix"], render["phaseSigns"])
    ]
    substitution = dict(zip(variables, coordinates))
    residual = sp.expand(original - displayed**power).subs(substitution, simultaneous=True)
    require(sp.expand(residual) == 0, "displayed polynomial does not power to D on this slice")
    require(
        sp.expand(displayed.subs(substitution, simultaneous=True)) != 0,
        "denominator vanishes identically on this slice",
    )


def validate_program(data, folder):
    def require(ok, message):
        if not ok:
            raise ValueError(f"{folder.name}: display divisor: {message}")

    require(
        data.get("schemaVersion") == 1 and data.get("kind") == "polynomial-program",
        "unknown format",
    )
    source = data.get("source", {})
    path = (folder / source.get("path", "")).resolve()
    require(path.is_relative_to(folder.resolve()) and path.is_file(), "missing local source")
    require(
        isinstance(source.get("definition"), str) and source["definition"],
        "missing source definition",
    )
    nodes = data.get("nodes")
    require(isinstance(nodes, list) and 0 < len(nodes) <= 4096, "invalid program size")
    degrees = []
    for node in nodes:
        require(isinstance(node, list) and len(node) in (2, 3), "invalid instruction")
        op, *args = node
        if op == "rational":
            require(len(args) == 1 and isinstance(args[0], str), "invalid rational")
            value = Fraction(args[0])
            require(math.isfinite(float(value)), "non-finite coefficient")
            degree = None if value == 0 else 0
        elif op == "sqrt":
            require(
                len(args) == 1 and type(args[0]) is int and 0 < abs(args[0]) <= 1000, "invalid radical"
            )
            degree = 0
        elif op == "variable":
            require(
                len(args) == 1 and type(args[0]) is int and 0 <= args[0] < 6, "invalid variable"
            )
            degree = 1
        else:
            require(op in ("add", "mul", "pow") and len(args) == 2, "invalid operation")
            references = args[:1] if op == "pow" else args
            require(
                all(type(i) is int and 0 <= i < len(degrees) for i in references),
                "invalid reference",
            )
            a = degrees[args[0]]
            if op == "pow":
                require(type(args[1]) is int and 1 <= args[1] <= 100, "invalid exponent")
                degree = None if a is None else a * args[1]
            else:
                b = degrees[args[1]]
                if op == "add":
                    require(a is None or b is None or a == b, "inhomogeneous sum")
                    degree = b if a is None else a
                else:
                    degree = None if a is None or b is None else a + b
        degrees.append(degree)
    output = data.get("output")
    require(type(output) is int and 0 <= output < len(nodes), "invalid output")
    require(
        type(data.get("degree")) is int and data["degree"] == degrees[output], "incorrect degree"
    )
    if "sliceIdentity" in data:
        require(max(d or 0 for d in degrees) <= 12, "slice identity program is too large")
    root = data.get("normalization", {}).get("signedRoot", 1)
    require(type(root) is int and 1 <= root <= 100, "invalid display normalization")
    gradient = data.get("normalization", {}).get("gradient", False)
    require(
        type(gradient) is bool and (not gradient or root == 1), "invalid gradient normalization"
    )
    return data

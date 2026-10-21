#!/usr/bin/env python3
"""Compare the display formula to the actual accepted Lean denominator definition."""
import ast
import json
from pathlib import Path
import re

import sympy as sp
from divisors import validate_program

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'data/one-reflection'
program = validate_program(json.loads((folder / 'display-divisor.json').read_text()), folder)
x = sp.symbols('X0 X1 X2 Y0 Y1 Y2')
source = (folder / 'Solution.lean').read_text()
section = source.split('namespace OneReflectionPhysical', 1)[1].split('end OneReflectionPhysical', 1)[0]
values = {f'X{i}': v for i, v in enumerate(x)} | {'tau': sp.sqrt(3)}


def arithmetic(node):
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return sp.Integer(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -arithmetic(node.operand)
    if isinstance(node, ast.BinOp):
        a, b = arithmetic(node.left), arithmetic(node.right)
        operations = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b, ast.Mult: lambda: a*b,
                      ast.Div: lambda: a/b, ast.Pow: lambda: a**b}
        return operations[type(node.op)]()
    raise ValueError(f'Unexpected expression: {ast.dump(node)}')


for name, expression in re.findall(r'^def (\w+) : Poly := (.+)$', section, re.M):
    expression = re.sub(r'X (\d)', r'X\1', expression).replace('^', '**')
    expression = re.sub(r'\bC\s*', '', expression)
    expression = expression.replace(': ℂ', '')
    values[name] = arithmetic(ast.parse(expression, mode='eval').body)
    if name == 'D':
        break
assert 'def fullD : Poly := D * sigma D' in source
assert 'def signs (i : Fin 6) : ℂ := if i.val = 1 ∨ i.val = 4 then -1 else 1' in source
expected = values['D'] * values['D'].subs({x[1]: -x[1], x[4]: -x[4]}, simultaneous=True)
calculated = []
for op, *args in program['nodes']:
    if op == 'variable': v = x[args[0]]
    elif op == 'rational': v = sp.Rational(args[0])
    elif op == 'sqrt': v = sp.sqrt(args[0])
    elif op == 'add': v = calculated[args[0]] + calculated[args[1]]
    elif op == 'mul': v = calculated[args[0]] * calculated[args[1]]
    elif op == 'pow': v = calculated[args[0]] ** args[1]
    calculated.append(v)
assert calculated[program['output']] == expected, 'Display formula differs from accepted Lean fullD'
# An independently proved specialization in the submission also checks the extraction.
t = sp.Symbol('t')
fiber = values['D'].subs(dict(zip(x, [1, 1, 1, 1, 1, t])))
assert sp.expand(fiber - (27972*t**18 + 391608*t**12 + 953312*t**6)) == 0

print('Display denominator equals Lean fullD exactly; degree 60 and proved fiber checked.')

folder = ROOT / 'data/two-ternary-dense-two-odd-hessian-d48'
program = validate_program(json.loads((folder/'display-divisor.json').read_text()), folder)
values = dict(zip(['X0','X1','X2','Y0','Y1','Y2'], x))
source = (folder/'PExplicitWitnessDefinitions.lean').read_text()
for name, expression in re.findall(r'^def (\w+) : SexticPoly := (.+)$', source, re.M):
    values[name] = arithmetic(ast.parse(expression.replace('^','**'), mode='eval').body)
    if name == 'D': break
expected = values['D']
calculated = []
for op, *args in program['nodes']:
    if op == 'variable': v = x[args[0]]
    elif op == 'rational': v = sp.Rational(args[0])
    elif op == 'add': v = calculated[args[0]] + calculated[args[1]]
    elif op == 'mul': v = calculated[args[0]] * calculated[args[1]]
    elif op == 'pow': v = calculated[args[0]] ** args[1]
    calculated.append(v)
assert calculated[program['output']] == expected
print('Hessian display denominator equals accepted ExplicitWitness.D exactly; degree 55.')

# A slice-specific root must be exactly the same zero set as the accepted D.
import copy
import yaml
from divisors import validate_slice_identity

folder = ROOT / 'data/hesse-radial-hesse-cofactor-d4-rational'
program = validate_program(json.loads((folder/'display-divisor.json').read_text()), folder)
denominator = yaml.safe_load((folder/'solution.rec').read_text())['witness']['D']
render = yaml.safe_load((folder/'instance.rec').read_text())['render']
validate_slice_identity(program, denominator, render, folder)

def must_reject(formula, witness, section):
    try:
        validate_slice_identity(formula, witness, section, folder)
    except ValueError:
        return
    raise AssertionError('An incorrect slice identity was accepted')

altered = copy.deepcopy(program)
altered['nodes'][4] = ['rational', '1/2']
must_reject(altered, denominator, render)
altered_plane = copy.deepcopy(render)
altered_plane['planeMatrix'][2][0] += 1e-12
must_reject(program, denominator, altered_plane)
altered_phase = copy.deepcopy(render)
altered_phase['phaseSigns'][2] *= -1
must_reject(program, denominator, altered_phase)
no_identity = copy.deepcopy(program)
no_identity.pop('sliceIdentity')
must_reject(no_identity, denominator, render)
zero_section = copy.deepcopy(render)
zero_section['planeMatrix'] = [[0]*4 for _ in range(6)]
must_reject(program, denominator, zero_section)
print('Hesse radial display root squares exactly to accepted D on its slice; changed formulas, slices, and phases are rejected.')

folder = ROOT / 'data/tie-offblock-ytype-d4-strict-rational'
program = validate_program(json.loads((folder/'display-divisor.json').read_text()), folder)
denominator = yaml.safe_load((folder/'solution.rec').read_text())['witness']['D']
render = yaml.safe_load((folder/'instance.rec').read_text())['render']
validate_slice_identity(program, denominator, render, folder)
# Independently verify the compact identity before imposing the real phases.
actual = sp.sympify(denominator['expression'], locals=dict(zip(map(str, x), x)))
assert sp.expand(actual.subs(x[4], x[0])-2*(3*x[0]**2+x[1]**2)**2) == 0
altered_phase = copy.deepcopy(render)
altered_phase['phaseSigns'][4] *= -1
must_reject(program, denominator, altered_phase)
print('Off-block tie display root squares exactly to accepted D on Y1=X0; changed relative phase is rejected.')

# Contact cone's six linear factors equal the full accepted denominator,
# independently of the selected real slice or camera.
folder = ROOT / 'data/contact46006'
program = validate_program(json.loads((folder/'display-divisor.json').read_text()), folder)
denominator = yaml.safe_load((folder/'solution.rec').read_text())['witness']['D']
render = yaml.safe_load((folder/'instance.rec').read_text())['render']
calculated = []
for op, *args in program['nodes']:
    if op == 'variable': v = x[args[0]]
    elif op == 'rational': v = sp.Rational(args[0])
    elif op == 'add': v = calculated[args[0]] + calculated[args[1]]
    elif op == 'mul': v = calculated[args[0]] * calculated[args[1]]
    calculated.append(v)
expected = sp.sympify(denominator['expression'], locals=dict(zip(map(str, x), x)))
assert sp.expand(calculated[program['output']] - expected) == 0
validate_slice_identity(program, denominator, render, folder)
altered = copy.deepcopy(program)
altered['nodes'][5] = ['rational', '-3']
must_reject(altered, denominator, render)
print('Contact cone factors equal accepted D exactly in all six variables; altered factors are rejected.')

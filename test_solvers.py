import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solver_pipeline.solvers.prolog_solver import run_prolog_solver
from solver_pipeline.solvers.z3_solver import run_z3_solver
from solver_pipeline.solvers.constraint_solver import run_constraint_solver
from solver_pipeline.solvers.prover9_solver import run_prover9_solver

def test_prolog():
    code = '''mortal(X) :- man(X).
man(socrates).

?- mortal(socrates).'''
    status, output = run_prolog_solver(code)
    print(f'Prolog Status: {status}\nOutput: {output}\n')

def test_z3():
    code = '''from z3 import *
s = Solver()
x = Int('x')
s.add(x > 5)
s.add(x < 10)
print(s.check())'''
    status, output = run_z3_solver(code)
    print(f'Z3 Status: {status}\nOutput: {output}\n')

def test_constraint():
    code = '''from constraint import *
problem = Problem()
problem.addVariable('a', [1, 2, 3])
problem.addVariable('b', [4, 5, 6])
problem.addConstraint(lambda a, b: a * 2 == b, ('a', 'b'))
solutions = problem.getSolutions()
print(solutions)'''
    status, output = run_constraint_solver(code)
    print(f'Constraint Status: {status}\nOutput: {output}\n')

def test_prover9():
    code = '''formulas(assumptions).
all x (Man(x) -> Mortal(x)).
Man(Socrates).
end_of_list.

formulas(goals).
Mortal(Socrates).
end_of_list.'''
    status, output = run_prover9_solver(code)
    print(f'Prover9 Status: {status}\nOutput: {output}\n')

if __name__ == '__main__':
    print('Testing Solvers...\n')
    try:
        test_prolog()
    except Exception as e:
         print(f'Prolog skip: {e}')
         
    try:
        test_z3()
    except Exception as e:
         print(f'Z3 skip: {e}')
         
    try:
         test_constraint()
    except Exception as e:
         print(f'Constraint skip: {e}')
         
    try:
         test_prover9()
    except Exception as e:
          print(f'Prover9 skip: {e}')

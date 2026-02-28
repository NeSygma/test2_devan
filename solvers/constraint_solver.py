import io
import contextlib

def run_constraint_solver(code: str) -> tuple[str, str]:
    """
    Executes Python code containing python-constraint logic.
    The code should define the problem, add variables, add constraints,
    and then print the result of problem.getSolutions() or similar.
    Returns:
        status: "True" (solutions found), "False/Uncertain" (no solutions), "Syntax Error", or "Execution Error"
        output: The raw standard output or error traceback.
    """
    code = code.replace("```python", "").replace("```", "").strip()
    
    # Capture standard output
    output_buffer = io.StringIO()
    
    # We execute the code in a dictionary context to avoid polluting globals
    exec_globals = {}
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, exec_globals)
        output = output_buffer.getvalue().strip()
        
        # If output includes solutions like [{'var': val}] or is just 'True'
        if output and not output.isspace() and output != "[]":
            return "True", output
        else:
            return "False/Uncertain", output
            
    except SyntaxError as e:
        return "Syntax Error", str(e)
    except Exception as e:
        return "Execution Error", str(e)

import io
import contextlib

def run_z3_solver(code: str) -> tuple[str, str]:
    """
    Executes Python code containing Z3 logic.
    The code should import z3, define the solver (e.g. s = Solver()), 
    add constraints, and print or return s.check().
    Returns:
        status: "True" (sat), "False/Uncertain" (unsat/unknown), "Syntax Error", or "Execution Error"
        output: Raw output string.
    """
    code = code.replace("```python", "").replace("```", "").strip()
    
    output_buffer = io.StringIO()
    # We must provide 'z3' in the globals if the LLM script assumes it, 
    # but it's safer to let the generated code import what it needs.
    exec_globals = {}
    
    try:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            # Execute the Z3 python code
            exec(code, exec_globals)
            
        output = output_buffer.getvalue().strip()
        
        # Determine status based on standard Z3 output
        if "sat" in output and "unsat" not in output:
             return "True", output
        elif "unsat" in output or "unknown" in output:
             return "False/Uncertain", output
        else:
             # If it didn't explicitly print sat/unsat, let's treat it cautiously
             return "Uncertain", output
             
    except SyntaxError as e:
        return "Syntax Error", str(e)
    except Exception as e:
        return "Execution Error", str(e)

import os
import subprocess
import re

# Local path configuration
PROVER9_BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'solver_model', 'Prover9', 'bin'))
PROVER9_BIN = os.path.join(PROVER9_BIN_DIR, 'prover9')

def to_wsl_path(win_path: str) -> str:
    """Converts 'D:\\path' to '/mnt/d/path'"""
    path = win_path.replace("\\", "/")
    if ":" in path:
        drive, rest = path.split(":", 1)
        return f"/mnt/{drive.lower()}{rest}"
    return path

def run_prover9_solver(code: str, timeout: int = 10) -> tuple[str, str]:
    """
    Executes Prover9 syntax logic via WSL.
    Returns:
        status: "True", "False/Uncertain", "Syntax Error", etc.
        output: Raw output from Prover9 execution.
    """
    code = code.replace("```prover9", "").replace("```", "").strip()
    
    # Text normalization
    code = code.replace("~", "-")
    code = code.replace("¬", "-")
    code = code.replace("^", " & ") 
    code = code.replace("∨", "|")
    code = code.replace("\\\\/", "|")
    code = code.replace("/\\\\", "&")
    code = code.replace("→", "->")
    code = code.replace("↔", "<->")
    code = code.replace("∀", "all ")
    code = code.replace("∃", "exists ")
    
    code = re.sub(r'\\bnot\\b', '-', code, flags=re.IGNORECASE)
    code = re.sub(r'\\band\\b', '&', code, flags=re.IGNORECASE)
    code = re.sub(r'\\bor\\b', '|', code, flags=re.IGNORECASE)
    code = re.sub(r'\\bimplies\\b', '->', code, flags=re.IGNORECASE)
    code = re.sub(r'\\biff\\b', '<->', code, flags=re.IGNORECASE)
    code = re.sub(r'\\bforall\\b', 'all', code, flags=re.IGNORECASE)

    code = code.replace("-exists", "- exists")
    code = code.replace("-all", "- all")
    code = code.replace(" v ", " | ")
    code = code.replace(")v(", ")|(")
    
    # Auto loop repair
    if "formulas(goals)" not in code and "formulas(assumptions)" in code:
        if "end_of_list." in code:
            parts = code.split("end_of_list.", 1)
            if len(parts) > 1:
                assumptions_part = parts[0] + "end_of_list."
                potential_goal = parts[1].strip()
                if potential_goal:
                    code = f"{assumptions_part}\\n\\nformulas(goals).\\n{potential_goal}\\nend_of_list."
                    
    input_filename = "temp_prover9.in"
    abs_input_path = os.path.abspath(input_filename)
    
    with open(abs_input_path, "w", encoding="utf-8") as f:
        f.write(code)

    wsl_bin_path = to_wsl_path(PROVER9_BIN)
    wsl_input_path = to_wsl_path(abs_input_path)

    command = ["wsl", wsl_bin_path, "-f", wsl_input_path]

    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            timeout=timeout
        )
        
        try:
            output = result.stdout.decode('utf-8', errors='replace')
        except:
            output = str(result.stdout)
            
        # Clean up temp file
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
            
        if "THEOREM PROVED" in output or "Exiting with 1 proof" in output:
            return "True", output
        elif "SEARCH FAILED" in output or "Exiting with failure" in output:
            return "False/Uncertain", output 
        else:
            if "Fatal error" in output or "syntax error" in output:
                 return "Syntax Error", output
            if result.returncode != 0 and not output:
                 err = result.stderr.decode('utf-8', errors='replace')
                 return "WSL Error", err
            return "Error", f"Exit Code: {result.returncode}\\nOutput: {output}"

    except subprocess.TimeoutExpired:
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
        return "Timeout", "Timed out"
    except Exception as e:
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
        return "Execution Error", str(e)

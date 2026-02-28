import os
import subprocess

def to_wsl_path(win_path: str) -> str:
    path = win_path.replace("\\\\", "/")
    if ":" in path:
        drive, rest = path.split(":", 1)
        return "/mnt/" + drive.lower() + rest
    return path

def run_prolog_solver(code: str, timeout: int = 10) -> tuple[str, str]:
    code = code.replace("```prolog", "").replace("```", "").strip()
    
    query = None
    kb_lines = []
    lines = code.split('\\n')
    for line in lines:
        if line.strip().startswith('?-'):
            query = line.strip()[2:].strip()
            if query.endswith('.'):
                query = query[:-1]
        else:
            kb_lines.append(line)
            
    kb_code = "\\n".join(kb_lines)
    
    input_filename = "temp_prolog.pl"
    abs_input_path = os.path.abspath(input_filename)
    
    with open(abs_input_path, "w", encoding="utf-8") as f:
        f.write(kb_code)

    if query:
        goal = "(" + query + " -> writeln('True'), halt ; writeln('False'), halt)"
    else:
        goal = "halt"

    wsl_input_path = to_wsl_path(abs_input_path)
    command = ["wsl", "swipl", "-q", "-g", goal, "-s", wsl_input_path]

    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            timeout=timeout
        )
        
        try:
            output = result.stdout.decode('utf-8', errors='replace').strip()
            err = result.stderr.decode('utf-8', errors='replace').strip()
        except Exception:
            output = str(result.stdout)
            err = str(result.stderr)
            
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
            
        full_out = (output + "\\n" + err).strip()
            
        if result.returncode != 0 and not full_out:
             win_command = ["swipl", "-q", "-g", goal, "-s", abs_input_path]
             try:
                 with open(abs_input_path, "w", encoding="utf-8") as f: f.write(kb_code)
                 win_res = subprocess.run(win_command, capture_output=True, timeout=timeout)
                 output = win_res.stdout.decode('utf-8', errors='replace').strip()
                 if os.path.exists(abs_input_path): os.remove(abs_input_path)
                 
                 if "True" in output:
                     return "True", output
                 else:
                     return "False/Uncertain", output
             except FileNotFoundError:
                 pass
                 
             return "Execution Error", "Could not execute via WSL or native swipl. Is SWI-Prolog installed?"

        if "True" in output:
            return "True", full_out
        elif "False" in output:
            return "False/Uncertain", full_out
        else:
            if "Syntax error" in err or "error" in err.lower():
                 return "Syntax Error", full_out
            return "Uncertain", full_out

    except subprocess.TimeoutExpired:
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
        return "Timeout", "Timed out"
    except Exception as e:
        if os.path.exists(abs_input_path):
            os.remove(abs_input_path)
        return "Execution Error", str(e)

# Problem Statement

Compile a quantum circuit with topology constraints. Given a set of quantum gates operating on 8 qubits arranged in a 2x4 grid topology, schedule the gates to minimize circuit depth and SWAP operations while respecting physical adjacency constraints and gate dependencies.

## Instance Data

**Qubits:** `q0`, `q1`, `q2`, `q3`, `q4`, `q5`, `q6`, `q7`

**Topology (2x4 grid adjacency):**
- Row 0: `q0-q1`, `q1-q2`, `q2-q3`
- Row 1: `q4-q5`, `q5-q6`, `q6-q7`
- Columns: `q0-q4`, `q1-q5`, `q2-q6`, `q3-q7`

**Mandatory Gates:**
1. `h_q0` - Single-qubit Hadamard gate on `q0`
2. `x_q1` - Single-qubit X gate on `q1`
3. `cnot_q2_q3` - CNOT gate on qubits `q2` (control), `q3` (target)
4. `cnot_q4_q5` - CNOT gate on qubits `q4` (control), `q5` (target)
5. `cnot_q0_q2` - CNOT gate on qubits `q0` (control), `q2` (target)
6. `toffoli_q5_q7_q6` - Toffoli gate with controls `q5`, `q7` and target `q6`

**Gate Dependencies:**
- `toffoli_q5_q7_q6` must be scheduled **strictly after** `cnot_q4_q5`

## Constraints

1. **Topology Constraint**: Multi-qubit gates can only operate on physically adjacent qubits according to the 2x4 grid topology
2. **SWAP Gates**: SWAP operations can be inserted between adjacent qubits to move logical qubits to required physical positions
3. **No Qubit Conflicts**: At each time step, each physical qubit can be used by at most one gate
4. **Dependency Ordering**: Gate dependencies must be respected in the schedule
5. **Toffoli Adjacency**: For Toffoli gates, both control qubits must be adjacent to the target qubit
6. **Complete Schedule**: All mandatory gates must be executed exactly once

## Objective

Find a solution that **minimizes circuit depth** (number of time steps). Among solutions with minimal depth, **minimize the number of SWAP gates**.

**Expected optimal: depth=3, swaps=1**

## Output Format

```json
{
  "circuit_depth": 3,
  "swaps_used": 1,
  "gate_schedule": [
    {
      "time": 1,
      "gates": ["cnot_q4_q5", "h_q0", "x_q1"]
    },
    {
      "time": 2,
      "gates": ["cnot_q2_q3", "swap_q0_q1"]
    },
    {
      "time": 3,
      "gates": ["cnot_q0_q2", "toffoli_q5_q7_q6"]
    }
  ]
}
```

**Field Descriptions:**
- `circuit_depth`: Integer - total number of time steps in the schedule
- `swaps_used`: Integer - total number of SWAP gates inserted
- `gate_schedule`: Array of time steps, each containing:
  - `time`: Integer - the time step number (1-indexed)
  - `gates`: Array of strings - gate names executed at this time step (sorted alphabetically)

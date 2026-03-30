# Problem Statement

Given a set of quantum gates that operate on qubits, schedule the gates to minimize circuit depth (number of time steps) while respecting qubit constraints. Gates can execute in parallel if they operate on disjoint qubit sets.

## Instance Data

**Qubits:** q0, q1, q2, q3

**Gates:**
- `h_q0`: Hadamard gate on q0
- `h_q1`: Hadamard gate on q1
- `x_q2`: Pauli-X gate on q2
- `cnot_q0_q1`: CNOT gate (control: q0, target: q1)
- `cnot_q1_q2`: CNOT gate (control: q1, target: q2)
- `cnot_q0_q3`: CNOT gate (control: q0, target: q3)

## Constraints

1. Each gate **must** be scheduled at exactly one time step
2. Two gates **cannot** execute at the same time if they share any qubit
3. **All** gates must be scheduled

## Objective

Find a schedule that **minimizes** the circuit depth (maximum time step used).

**Expected optimal depth:** 3

## Output Format

```json
{
  "circuit_depth": 3,
  "gate_schedule": [
    {"time": 1, "gates": ["h_q0", "h_q1", ...]},
    {"time": 2, "gates": ["cnot_q0_q1", ...]},
    ...
  ]
}
```

**Fields:**
- `circuit_depth` (integer): The minimum number of time steps required
- `gate_schedule` (list): For each time step, which gates execute
  - `time` (integer): The time step (1, 2, 3, ...)
  - `gates` (list of strings): Gate names executing at this time step

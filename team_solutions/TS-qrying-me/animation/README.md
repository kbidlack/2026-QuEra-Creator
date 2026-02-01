# QuEra Circuit Compilation Stack Animation

Our submission is an animation that precisely demonstrates how a quantum circuit flows through QuEra's SDK stack, from logical representation down to hardware-level atom execution. The process we depict starts at the logical level, where circuits are expressed by abstract (logical) qubits with structured control flow (SQuIN semantics), then shows gate lowering, where non-native operations (like CNOT) are rewritten into native atom interactions (CZ plus basis changes) and visualized as a concrete pulse protocol. From there, we show one big part of neutral-atom computing: spatiotemporal compilation, where the compiler must route atoms themselves by moving them between different zones using optical tweezers. Next, we show how these scheduled moves and entangling moments become control at the pulse level, where laser intensity and detuning are controlled.

Our approach emphasizes each stage as a "layer" which is animated with [quantum-animation-toolbox](https://github.com/jwaldorf05/quantum-animation-toolbox) and can be run with any valid SQuIN kernel. [main.py](file://./main.py) runs each layer which is contained in a different file starting with `layern_`. [core.py](file://./core.py) contains some helpful Python classes and other utils.

To run the animation, in this directory run:

```
uv run manimgl main.py BellStateDemo # or choose another circuit, like GHZCircuitDemo
```

alternatively, if you prefer a video output:

```
uv run manimgl main.py BellStateDemo -w
```

will output BellStateDemo.mp4 to `./videos`

## Future Work

- Drive the animation directly from real compiler artifacts. Right now we have it structured to match the stack, but we aren't actually running any bloqade code--we animate what we studied about the compiler, rather than using what it produces.
- Extend and improve depicted processes. Currently we have just a few shown, like Rydberg blockade entanglement and pulse control, but it would be nice to go in more detail or add more steps.

## File Structure

The animation is split into core.py, main.py and five layer files.

```
animation/
├── core.py                 # Shared components (CircuitDefinition, visual primitives)
├── layer1_logical.py       # Layer 1: Logical circuit representation
├── layer2_decomposition.py # Layer 2: Gate decomposition to native gates
├── layer3_spatial.py       # Layer 3: Spatial routing with bloqade-lanes
├── layer4_pulse.py         # Layer 4: Pulse-level control with bloqade-analog
├── layer5_hardware.py      # Layer 5: Hardware execution on Rydberg atoms
├── main.py                 # Main orchestrator and example circuits
└── __init__.py             # Package exports
```

## The Abstraction Layers

The animation visualizes the following layers of the QuEra compilation stack:

### Layer 1: Logical Circuit (bloqade-circuit + SQuIN)

- High-level quantum circuit with logical qubits
- SQuIN IR retains structured control flow (loops, conditionals)
- Qubits are abstract handles - no physical location yet

### Layer 2: Gate Decomposition

- CNOT gates decomposed to native CZ + Hadamards
- Levine-Pichler protocol for CZ implementation:
  - π pulse on Control (excite to Rydberg)
  - 2π pulse on Target (conditional rotation)
  - π pulse on Control (de-excite)

### Layer 3: Spatial Routing (bloqade-lanes)

- Physical atom placement in zones:
  - **Storage Zone**: Atoms parked with large separation
  - **Entangling Zone**: Atoms brought close for Rydberg blockade
  - **Readout Zone**: Measurement via fluorescence
- Optical tweezers transport atoms between zones
- Move operations have duration, velocity profiles, heating costs

### Layer 4: Pulse Control (bloqade-analog)

- Time-dependent Hamiltonian: H(t) = (ℏ/2)Ω(t)σx - ℏΔ(t)n + Vᵢⱼnᵢnⱼ
- Waveform shapes (Blackman windows) for adiabatic control
- Rabi frequency controls laser intensity
- Detuning controls laser frequency

### Layer 5: Hardware Execution

- Rubidium-87 atoms in optical tweezers
- Rydberg excitation creates blockade effect
- Entanglement through conditional phase accumulation
- Measurement via fluorescence detection

## Usage

### Run the Full Animation

```bash
# GHZ State (3 qubits)
uv run manimgl main.py GHZCircuitDemo

# Bell State (2 qubits)
uv run manimgl main.py BellStateDemo

# 4-Qubit Star Entanglement
uv run manimgl main.py FourQubitDemo

# QFT-style Circuit
uv run manimgl main.py BellStateDemo

# Custom circuit (edit main.py to customize, or you can add your own!)
uv run manimgl main.py CustomCircuitDemo
```

### Run individual layers for testing

```bash
manimgl layer1_logical.py Layer1Demo
manimgl layer2_decomposition.py Layer2Demo
manimgl layer3_spatial.py Layer3Demo
manimgl layer4_pulse.py Layer4Demo
manimgl layer5_hardware.py Layer5Demo
```

### Create your own circuit

Edit `CustomCircuitDemo.get_circuit()` in `main.py`, or create a new class:

```python
from main import CompilationAnimation
from core import CircuitDefinition

class MyCircuitDemo(CompilationAnimation):
    def get_circuit(self) -> CircuitDefinition:
        circuit = CircuitDefinition(num_qubits=3, name="My Circuit")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cz(1, 2)
        circuit.measure_all()
        return circuit
```

Then run:

```bash
uv run manimgl main.py MyCircuitDemo
```

### Import from Bloqade Kernel

You can import circuits directly from bloqade squin kernels:

```python
from bloqade import squin
from core import CircuitDefinition

@squin.kernel
def ghz_state():
    q = squin.qalloc(3)
    squin.h(q[0])
    squin.cx(q[0], q[1])
    squin.cx(q[1], q[2])

# Convert to animation circuit
circuit = CircuitDefinition.from_bloqade(ghz_state, name="GHZ State")
```

### Import from Cirq Circuit

You can also import from cirq circuits:

```python
import cirq
from core import CircuitDefinition

q = cirq.LineQubit.range(2)
cirq_circuit = cirq.Circuit(
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1])
)

circuit = CircuitDefinition.from_cirq(cirq_circuit, name="Bell State")
```

## Available Gates

The `CircuitDefinition` class supports:

- Single-qubit: `h`, `x`, `y`, `z`, `s`, `t`, `rx`, `ry`, `rz`
- Two-qubit: `cx`/`cnot`, `cz`, `swap`
- Three-qubit: `ccx` (Toffoli)
- Measurement: `measure`, `measure_all`

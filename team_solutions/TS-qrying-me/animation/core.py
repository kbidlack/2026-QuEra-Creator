"""
Core components shared across all animation layers.

This module contains:
- CircuitDefinition: Define quantum circuits
- Visual components (ExplanationBox, CodeBlock, etc.)
- ManimGL compatibility fixes
- Color constants
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple

from manimlib import *

# manimgl compatibility

try:
    _test = GREY_B
    GRAY_B = GREY_B
except NameError:
    try:
        _test = GRAY_B
    except NameError:
        GRAY_B = "#888888"

try:
    _test = Create
except NameError:
    Create = ShowCreation

try:
    _test = GrowArrow
except NameError:
    GrowArrow = ShowCreation

# quera brand colors
QUERA_PURPLE = "#6B4E9B"
QUERA_BLUE = "#3B82F6"
QUERA_RED = "#EF4444"
QUERA_YELLOW = "#F59E0B"
QUERA_GREEN = "#10B981"
QUERA_GRAY = "#6B7280"
QUERA_ORANGE = "#F97316"


class GateType(Enum):
    H = "H"
    X = "X"
    Y = "Y"
    Z = "Z"
    S = "S"
    T = "T"
    RX = "RX"
    RY = "RY"
    RZ = "RZ"
    CX = "CX"
    CZ = "CZ"
    SWAP = "SWAP"
    CCX = "CCX"
    MEASURE = "M"


@dataclass
class Gate:
    """Represents a quantum gate operation."""

    gate_type: GateType
    qubits: Tuple[int, ...]
    params: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_single_qubit(self) -> bool:
        return self.gate_type in {
            GateType.H,
            GateType.X,
            GateType.Y,
            GateType.Z,
            GateType.S,
            GateType.T,
            GateType.RX,
            GateType.RY,
            GateType.RZ,
            GateType.MEASURE,
        }

    @property
    def is_two_qubit(self) -> bool:
        return self.gate_type in {GateType.CX, GateType.CZ, GateType.SWAP}


class CircuitDefinition:
    """
    Define a quantum circuit for animation.

    Example (manual definition):
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

    Example (from bloqade kernel):
        from bloqade import squin

        @squin.kernel
        def ghz():
            q = squin.qalloc(3)
            squin.h(q[0])
            squin.cx(q[0], q[1])
            squin.cx(q[1], q[2])

        circuit = CircuitDefinition.from_bloqade(ghz, name="GHZ State")

    Example (from cirq circuit):
        import cirq
        q = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit(cirq.H(q[0]), cirq.CNOT(q[0], q[1]))
        circuit = CircuitDefinition.from_cirq(cirq_circuit, name="Bell State")
    """

    def __init__(self, num_qubits: int, name: str = "Quantum Circuit"):
        self.num_qubits = num_qubits
        self.name = name
        self.gates: List[Gate] = []
        self._source_kernel = None  # if available, store original bloqade kernel

    @classmethod
    def from_bloqade(cls, kernel, name: str = "Bloqade Circuit") -> "CircuitDefinition":
        """
        Create a CircuitDefinition from a bloqade squin kernel.

        This converts the kernel to a cirq circuit internally, then extracts gates.

        Args:
            kernel: A bloqade squin kernel decorated with @squin.kernel
            name: Name for the circuit

        Returns:
            CircuitDefinition with gates extracted from the kernel

        Example:
            from bloqade import squin

            @squin.kernel
            def bell_state():
                q = squin.qalloc(2)
                squin.h(q[0])
                squin.cx(q[0], q[1])

            circuit = CircuitDefinition.from_bloqade(bell_state, name="Bell State")
        """
        try:
            from bloqade import cirq_utils
        except ImportError:
            raise ImportError(
                "bloqade is required for from_bloqade(). "
                "Install with: pip install bloqade"
            )

        # convert bloqade kernel to cirq circuit
        cirq_circuit = cirq_utils.emit_circuit(kernel)
        circuit = cls.from_cirq(cirq_circuit, name=name)
        circuit._source_kernel = kernel  # Store for get_squin_code()
        return circuit

    @classmethod
    def from_cirq(cls, cirq_circuit, name: str = "Cirq Circuit") -> "CircuitDefinition":
        """
        Create a CircuitDefinition from a cirq Circuit.

        Args:
            cirq_circuit: A cirq.Circuit object
            name: Name for the circuit

        Returns:
            CircuitDefinition with gates extracted from the cirq circuit

        Example:
            import cirq
            q = cirq.LineQubit.range(2)
            circuit = cirq.Circuit(cirq.H(q[0]), cirq.CNOT(q[0], q[1]))
            defn = CircuitDefinition.from_cirq(circuit, name="Bell")
        """
        try:
            import cirq
        except ImportError:
            raise ImportError(
                "cirq is required for from_cirq(). Install with: pip install cirq"
            )

        # get all qubits and create index mapping
        all_qubits = sorted(cirq_circuit.all_qubits())
        qubit_to_idx = {q: i for i, q in enumerate(all_qubits)}
        num_qubits = len(all_qubits)

        circuit = cls(num_qubits=num_qubits, name=name)

        # gate type mapping from cirq -> GateType
        for moment in cirq_circuit:
            for op in moment:
                gate = op.gate
                qubits = tuple(qubit_to_idx[q] for q in op.qubits)

                # single-qubit gates
                if isinstance(gate, cirq.HPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.H, qubits))
                elif isinstance(gate, cirq.XPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.X, qubits))
                elif isinstance(gate, cirq.YPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.Y, qubits))
                elif isinstance(gate, cirq.ZPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.Z, qubits))
                elif isinstance(gate, cirq.ZPowGate) and gate.exponent == 0.5:
                    circuit.gates.append(Gate(GateType.S, qubits))
                elif isinstance(gate, cirq.ZPowGate) and gate.exponent == 0.25:
                    circuit.gates.append(Gate(GateType.T, qubits))
                elif isinstance(gate, cirq.Rx):
                    circuit.gates.append(
                        Gate(GateType.RX, qubits, {"angle": gate.rads})
                    )
                elif isinstance(gate, cirq.Ry):
                    circuit.gates.append(
                        Gate(GateType.RY, qubits, {"angle": gate.rads})
                    )
                elif isinstance(gate, cirq.Rz):
                    circuit.gates.append(
                        Gate(GateType.RZ, qubits, {"angle": gate.rads})
                    )
                # two-qubit gates
                elif isinstance(gate, cirq.CXPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.CX, qubits))
                elif isinstance(gate, cirq.CZPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.CZ, qubits))
                elif isinstance(gate, cirq.SwapPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.SWAP, qubits))
                # three-qubit gates
                elif isinstance(gate, cirq.CCXPowGate) and gate.exponent == 1:
                    circuit.gates.append(Gate(GateType.CCX, qubits))
                # measurement
                elif isinstance(gate, cirq.MeasurementGate):
                    for q in qubits:
                        circuit.gates.append(Gate(GateType.MEASURE, (q,)))
                # fallback for other gates - try to identify by name
                else:
                    gate_name = type(gate).__name__.upper()
                    if "CNOT" in gate_name or gate_name == "CX":
                        circuit.gates.append(Gate(GateType.CX, qubits))
                    elif gate_name == "CZ":
                        circuit.gates.append(Gate(GateType.CZ, qubits))
                    elif gate_name == "H":
                        circuit.gates.append(Gate(GateType.H, qubits))
                    # Skip unrecognized gates with a warning
                    else:
                        import warnings

                        warnings.warn(f"Skipping unrecognized gate: {gate}")

        return circuit

    def h(self, qubit: int) -> "CircuitDefinition":
        """Add Hadamard gate."""
        self.gates.append(Gate(GateType.H, (qubit,)))
        return self

    def x(self, qubit: int) -> "CircuitDefinition":
        """Add Pauli-X gate."""
        self.gates.append(Gate(GateType.X, (qubit,)))
        return self

    def y(self, qubit: int) -> "CircuitDefinition":
        """Add Pauli-Y gate."""
        self.gates.append(Gate(GateType.Y, (qubit,)))
        return self

    def z(self, qubit: int) -> "CircuitDefinition":
        """Add Pauli-Z gate."""
        self.gates.append(Gate(GateType.Z, (qubit,)))
        return self

    def s(self, qubit: int) -> "CircuitDefinition":
        """Add S gate."""
        self.gates.append(Gate(GateType.S, (qubit,)))
        return self

    def t(self, qubit: int) -> "CircuitDefinition":
        """Add T gate."""
        self.gates.append(Gate(GateType.T, (qubit,)))
        return self

    def rx(self, qubit: int, angle: float) -> "CircuitDefinition":
        """Add RX rotation gate."""
        self.gates.append(Gate(GateType.RX, (qubit,), {"angle": angle}))
        return self

    def ry(self, qubit: int, angle: float) -> "CircuitDefinition":
        """Add RY rotation gate."""
        self.gates.append(Gate(GateType.RY, (qubit,), {"angle": angle}))
        return self

    def rz(self, qubit: int, angle: float) -> "CircuitDefinition":
        """Add RZ rotation gate."""
        self.gates.append(Gate(GateType.RZ, (qubit,), {"angle": angle}))
        return self

    def cx(self, control: int, target: int) -> "CircuitDefinition":
        """Add CNOT gate."""
        self.gates.append(Gate(GateType.CX, (control, target)))
        return self

    def cnot(self, control: int, target: int) -> "CircuitDefinition":
        """Alias for cx."""
        return self.cx(control, target)

    def cz(self, control: int, target: int) -> "CircuitDefinition":
        """Add CZ gate."""
        self.gates.append(Gate(GateType.CZ, (control, target)))
        return self

    def swap(self, qubit1: int, qubit2: int) -> "CircuitDefinition":
        """Add SWAP gate."""
        self.gates.append(Gate(GateType.SWAP, (qubit1, qubit2)))
        return self

    def ccx(self, control1: int, control2: int, target: int) -> "CircuitDefinition":
        """Add Toffoli gate."""
        self.gates.append(Gate(GateType.CCX, (control1, control2, target)))
        return self

    def measure(self, qubit: int) -> "CircuitDefinition":
        """Add measurement on a single qubit."""
        self.gates.append(Gate(GateType.MEASURE, (qubit,)))
        return self

    def measure_all(self) -> "CircuitDefinition":
        """Add measurement on all qubits."""
        for q in range(self.num_qubits):
            self.measure(q)
        return self

    def get_squin_code(self) -> str:
        """
        Get SQuIN-style code representation.

        If the circuit was created from a bloqade kernel, returns the actual
        source code of that kernel. Otherwise, generates equivalent code.
        """
        # if we have the original kernel, extract its source code
        if self._source_kernel is not None:
            try:
                import inspect
                import textwrap

                func = getattr(self._source_kernel, "py_func", self._source_kernel)
                source = inspect.getsource(func)
                return textwrap.dedent(source)
            except (OSError, TypeError):
                pass  # fall back to generated code

        lines = [
            "@squin.kernel",
            f"def {self.name.lower().replace(' ', '_')}():",
            f"    q = squin.qalloc({self.num_qubits})",
        ]
        for gate in self.gates:
            if gate.gate_type == GateType.H:
                lines.append(f"    squin.h(q[{gate.qubits[0]}])")
            elif gate.gate_type == GateType.X:
                lines.append(f"    squin.x(q[{gate.qubits[0]}])")
            elif gate.gate_type == GateType.CX:
                lines.append(f"    squin.cx(q[{gate.qubits[0]}], q[{gate.qubits[1]}])")
            elif gate.gate_type == GateType.CZ:
                lines.append(f"    squin.cz(q[{gate.qubits[0]}], q[{gate.qubits[1]}])")
        if any(g.gate_type == GateType.MEASURE for g in self.gates):
            lines.append("    return squin.measure(q)")
        return "\n".join(lines)

    def get_native_decomposition(self) -> List[Gate]:
        """Decompose circuit to native QuEra gates (CZ + single-qubit rotations)."""
        native_gates = []
        for gate in self.gates:
            if gate.gate_type == GateType.CX:
                control, target = gate.qubits
                native_gates.append(Gate(GateType.H, (target,)))
                native_gates.append(Gate(GateType.CZ, (control, target)))
                native_gates.append(Gate(GateType.H, (target,)))
            elif gate.gate_type == GateType.SWAP:
                q1, q2 = gate.qubits
                for _ in range(3):
                    native_gates.append(Gate(GateType.H, (q2,)))
                    native_gates.append(Gate(GateType.CZ, (q1, q2)))
                    native_gates.append(Gate(GateType.H, (q2,)))
            else:
                native_gates.append(gate)
        return native_gates

    def get_cz_layers(self) -> List[List[Gate]]:
        """Group CZ gates into parallel execution layers."""
        native = self.get_native_decomposition()
        cz_gates = [g for g in native if g.gate_type == GateType.CZ]
        layers = []
        used_qubits = set()
        current_layer = []
        for gate in cz_gates:
            gate_qubits = set(gate.qubits)
            if gate_qubits & used_qubits:
                if current_layer:
                    layers.append(current_layer)
                current_layer = [gate]
                used_qubits = gate_qubits
            else:
                current_layer.append(gate)
                used_qubits |= gate_qubits
        if current_layer:
            layers.append(current_layer)
        return layers


class ExplanationBox(VGroup):
    """A text box for explanations that appears on the side."""

    def __init__(self, text, width=3.5, font_size=14, color=WHITE, **kwargs):
        super().__init__(**kwargs)

        lines = []
        max_chars = int(width * 8)

        for paragraph in text.split("\n"):
            words = paragraph.split()
            current_line = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 <= max_chars:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
            if current_line:
                lines.append(" ".join(current_line))
            elif not words:
                lines.append("")  # preserve empty lines

        text_group = VGroup()
        for line in lines:
            text_line = Text(line, font_size=font_size, color=color)
            text_group.add(text_line)
        text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.08)

        bg = SurroundingRectangle(
            text_group,
            buff=0.15,
            stroke_color=color,
            stroke_width=1,
            fill_color=BLACK,
            fill_opacity=0.9,
        )
        self.add(bg, text_group)
        self.text_group = text_group
        self.background = bg


class CodeBlock(VGroup):
    """Simple code block display with proper tab/indentation handling."""

    def __init__(self, code, font_size=14, stroke_color=WHITE, tab_width=4, **kwargs):
        super().__init__(**kwargs)
        # convert tabs to spaces for consistent display
        code = code.replace("\t", " " * tab_width)
        lines = code.strip().split("\n")

        # calculate character width using a reference character
        ref_char = Text("M", font_size=font_size, font="Menlo")
        char_width = ref_char.get_width()

        text_lines = VGroup()
        for line in lines:
            # count leading spaces for indentation
            stripped = line.lstrip(" ")
            indent_count = len(line) - len(stripped)

            display_line = stripped if stripped else " "
            text_line = Text(display_line, font_size=font_size, font="Menlo")

            # store indent info for later
            text_line.indent_offset = indent_count * char_width
            text_lines.add(text_line)

        text_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.06)

        for text_line in text_lines:
            text_line.shift(RIGHT * text_line.indent_offset)

        bg = SurroundingRectangle(
            text_lines,
            buff=0.15,
            stroke_color=stroke_color,
            stroke_width=2,
            fill_color=BLACK,
            fill_opacity=0.9,
        )
        self.add(bg, text_lines)


class LayerLabel(VGroup):
    """A styled label for each abstraction layer."""

    def __init__(self, title, subtitle, color=WHITE, **kwargs):
        super().__init__(**kwargs)
        self.title_text = Text(title, font_size=24, color=color, weight=BOLD)
        self.subtitle_text = Text(subtitle, font_size=14, color=GRAY_B)
        self.subtitle_text.next_to(self.title_text, DOWN, buff=0.08)
        self.add(self.title_text, self.subtitle_text)


class ZoneBox(VGroup):
    """A labeled zone region."""

    def __init__(self, width, height, label, color, **kwargs):
        super().__init__(**kwargs)
        self.box = Rectangle(
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2,
            fill_color=color,
            fill_opacity=0.1,
        )
        self.label = Text(label, font_size=14, color=color)
        self.label.next_to(self.box, UP, buff=0.08)
        self.add(self.box, self.label)


class AnimatedQubit(VGroup):
    """Qubit with animation capabilities."""

    def __init__(self, position=ORIGIN, radius=0.15, color=QUERA_PURPLE, **kwargs):
        super().__init__(**kwargs)
        self.dot = Dot(point=position, radius=radius, color=color)
        self.glow = Circle(
            radius=radius * 2.5, stroke_width=0, fill_color=color, fill_opacity=0.25
        )
        self.glow.move_to(position)
        self.add(self.glow, self.dot)
        self._base_color = color

    def pulse_once(self, run_time=0.5):
        return Succession(
            self.glow.animate.scale(1.4).set_opacity(0.5),
            self.glow.animate.scale(1 / 1.4).set_opacity(0.25),
            run_time=run_time,
        )

    def set_color_animated(self, new_color):
        return AnimationGroup(
            self.dot.animate.set_color(new_color),
            self.glow.animate.set_color(new_color),
        )

    def excite(self):
        """Animate excitation to Rydberg state."""
        return self.set_color_animated(QUERA_RED)

    def deexcite(self):
        """Animate return to ground state."""
        return self.set_color_animated(self._base_color)


class CircuitVisual(VGroup):
    """Visual representation of a quantum circuit."""

    def __init__(
        self,
        circuit: CircuitDefinition,
        wire_length=None,
        wire_spacing=0.7,
        slot_width=0.6,
        padding=0.4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.circuit = circuit
        self.wire_spacing = wire_spacing
        self.slot_width = slot_width
        self.padding = padding

        # auto-calculate wire length based on number of gates
        num_gates = len(circuit.gates)
        if wire_length is None:
            self.wire_length = num_gates * slot_width + 2 * padding
        else:
            self.wire_length = wire_length

        self.wires = VGroup()
        self.labels = VGroup()
        self.gates = VGroup()

        for i in range(circuit.num_qubits):
            y = -i * wire_spacing
            wire = Line(
                LEFT * self.wire_length / 2,
                RIGHT * self.wire_length / 2,
                color=WHITE,
                stroke_width=2,
            )
            wire.shift(UP * y)
            self.wires.add(wire)
            label = Tex(f"|q_{i}\\rangle", font_size=18)
            label.next_to(wire, LEFT, buff=0.15)
            self.labels.add(label)

        self.wires.set_z_index(0)
        self.gates.set_z_index(5)
        self.add(self.wires, self.labels, self.gates)
        self._current_slot = 0

    def _get_slot_x(self, slot):
        return -self.wire_length / 2 + self.padding + (slot + 0.5) * self.slot_width

    def _get_wire_y(self, qubit):
        return -qubit * self.wire_spacing

    def add_gate_visual(self, gate: Gate) -> VGroup:
        """Add visual representation of a gate."""
        slot = self._current_slot
        if gate.gate_type == GateType.H:
            visual = self._create_single_gate("H", gate.qubits[0], slot)
        elif gate.gate_type == GateType.X:
            visual = self._create_single_gate("X", gate.qubits[0], slot)
        elif gate.gate_type == GateType.Y:
            visual = self._create_single_gate("Y", gate.qubits[0], slot)
        elif gate.gate_type == GateType.Z:
            visual = self._create_single_gate("Z", gate.qubits[0], slot)
        elif gate.gate_type == GateType.CX:
            visual = self._create_cnot(gate.qubits[0], gate.qubits[1], slot)
        elif gate.gate_type == GateType.CZ:
            visual = self._create_cz(gate.qubits[0], gate.qubits[1], slot)
        elif gate.gate_type == GateType.MEASURE:
            visual = self._create_measurement(gate.qubits[0], slot)
        else:
            visual = self._create_single_gate("?", gate.qubits[0], slot)
        visual.set_z_index(5)
        self.gates.add(visual)
        self._current_slot += 1
        return visual

    def _create_single_gate(self, label, qubit, slot):
        x, y = self._get_slot_x(slot), self._get_wire_y(qubit)
        return VGroup(
            Square(
                side_length=0.4, fill_color=BLACK, fill_opacity=1, stroke_color=WHITE
            ),
            Text(label, font_size=16, color=WHITE),
        ).move_to([x, y, 0])

    def _create_cnot(self, control, target, slot):
        x = self._get_slot_x(slot)
        cy, ty = self._get_wire_y(control), self._get_wire_y(target)
        return VGroup(
            Line([x, cy, 0], [x, ty, 0], color=WHITE, stroke_width=2),
            Dot(point=[x, cy, 0], radius=0.07, color=WHITE),
            Circle(radius=0.12, stroke_color=WHITE, stroke_width=2).move_to([x, ty, 0]),
            Line(LEFT * 0.08, RIGHT * 0.08, color=WHITE).move_to([x, ty, 0]),
            Line(UP * 0.08, DOWN * 0.08, color=WHITE).move_to([x, ty, 0]),
        )

    def _create_cz(self, control, target, slot):
        x = self._get_slot_x(slot)
        cy, ty = self._get_wire_y(control), self._get_wire_y(target)
        return VGroup(
            Line([x, cy, 0], [x, ty, 0], color=WHITE, stroke_width=2),
            Dot(point=[x, cy, 0], radius=0.07, color=WHITE),
            Dot(point=[x, ty, 0], radius=0.07, color=WHITE),
        )

    def _create_measurement(self, qubit, slot):
        x, y = self._get_slot_x(slot), self._get_wire_y(qubit)
        return VGroup(
            Square(
                side_length=0.4, fill_color=BLACK, fill_opacity=1, stroke_color=WHITE
            ),
            Arc(start_angle=PI, angle=-PI, radius=0.1, stroke_color=WHITE).shift(
                DOWN * 0.02
            ),
            Line(ORIGIN, UP * 0.1 + RIGHT * 0.06, color=WHITE, stroke_width=2),
        ).move_to([x, y, 0])

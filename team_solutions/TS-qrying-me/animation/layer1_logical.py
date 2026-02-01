"""
Layer 1: Logical Circuit

This layer shows the high-level quantum circuit as the user defines it.
Qubits are abstract handles - no physical location yet.

Key concepts visualized:
- Circuit diagram with gates (H, CNOT, CZ, etc.)
- SQuIN IR code representation
- Kirin compiler transformation
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from core import (
    QUERA_BLUE,
    QUERA_ORANGE,
    QUERA_YELLOW,
    CircuitDefinition,
    CircuitVisual,
    CodeBlock,
    Create,
    ExplanationBox,
    GateType,
    LayerLabel,
)
from manimlib import *


def show_logical_layer(scene: Scene, circuit: CircuitDefinition):
    """
    Animate Layer 1: Logical Circuit representation.

    Args:
        scene: The Manim scene to animate in
        circuit: The circuit definition to visualize

    Returns:
        None (cleans up after itself)
    """
    label = LayerLabel(
        "Layer 1: Logical Circuit", "bloqade-circuit + SQuIN IR", color=QUERA_BLUE
    )
    label.to_corner(UL, buff=0.3)
    scene.play(FadeIn(label))

    explanation = ExplanationBox(
        "The journey begins with your quantum algorithm expressed as a logical circuit. "
        "At this level, qubits are abstract handles - they have no physical location yet. "
        "The circuit uses familiar gates like Hadamard (H) and CNOT (CX).",
        width=3.2,
        font_size=13,
        color=QUERA_BLUE,
    )
    explanation.to_edge(RIGHT, buff=0.3).shift(UP * 1.5)
    scene.play(FadeIn(explanation))

    circuit_vis = CircuitVisual(circuit, wire_spacing=0.65)
    circuit_vis.shift(LEFT * 1.5 + UP * 1.0)

    scene.play(Create(circuit_vis.wires), Write(circuit_vis.labels))
    scene.wait(0.5)

    gate_explanations = {
        GateType.H: "Hadamard: Creates superposition",
        GateType.X: "Pauli-X: Bit flip",
        GateType.Y: "Pauli-Y: Bit + phase flip",
        GateType.Z: "Pauli-Z: Phase flip",
        GateType.CX: "CNOT: Can entangle two qubits",
        GateType.CZ: "CZ: Controlled phase",
        GateType.MEASURE: "Measurement",
    }

    explained_gate_types = set()

    for gate in circuit.gates:
        gate_vis = circuit_vis.add_gate_visual(gate).shift(LEFT * 1.5 + UP * 1.0)

        if (
            gate.gate_type in gate_explanations
            and gate.gate_type not in explained_gate_types
            and len(explained_gate_types) < 3
        ):
            explained_gate_types.add(gate.gate_type)
            gate_note = Text(
                gate_explanations[gate.gate_type], font_size=11, color=QUERA_YELLOW
            )
            gate_note.next_to(gate_vis, DOWN, buff=0.3)
            scene.play(FadeIn(gate_vis, scale=0.5), FadeIn(gate_note), run_time=0.5)
            scene.wait(0.8)
            scene.play(FadeOut(gate_note), run_time=0.3)
        else:
            scene.play(FadeIn(gate_vis, scale=0.5), run_time=0.25)

    scene.wait(0.5)

    scene.play(FadeOut(explanation))

    squin_explanation = ExplanationBox(
        "Kirin compiles your circuit into SQuIN IR (Structural Quantum Instruction Set). "
        "Unlike flat assembly languages, SQuIN preserves program structure - "
        "loops and conditionals remain intact for better optimization and SIMD broadcasting.",
        width=3.2,
        font_size=13,
        color=QUERA_BLUE,
    )
    squin_explanation.to_edge(RIGHT, buff=0.3).shift(UP * 1.5)

    squin_code = CodeBlock(
        circuit.get_squin_code(), font_size=11, stroke_color=QUERA_BLUE
    )
    squin_code.to_edge(RIGHT, buff=0.3).shift(DOWN * 1)
    squin_code.scale(0.8)

    scene.play(FadeIn(squin_explanation), FadeIn(squin_code))
    scene.wait(2.5)

    key_point = ExplanationBox(
        "KEY INSIGHT: At this layer, q[0], q[1], q[2] are just logical handles. "
        "They have no physical location - mapping to real atoms happens in Layer 3!",
        width=4,
        font_size=12,
        color=QUERA_ORANGE,
    )
    key_point.to_edge(DOWN, buff=0.3)
    scene.play(FadeIn(key_point))
    scene.wait(2.0)

    all_elements = VGroup(label, circuit_vis, squin_explanation, squin_code, key_point)
    scene.play(FadeOut(all_elements))


class Layer1Demo(Scene):
    """Standalone demo of Layer 1."""

    def construct(self):
        # Create a sample circuit
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        show_logical_layer(self, circuit)

"""
Layer 2: Gate Decomposition

This layer shows how abstract gates are decomposed into native QuEra operations.
The key transformation: CNOT -> H . CZ . H

Key concepts visualized:
- The native entangling interaction is a Rydberg-blockade controlled phase (often compiled as CZ up to phases).
- Rydberg blockade pulse sequence for CZ implementation (simplified 3-pulse protocol)
- Parallel gate scheduling into layers
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from core import (
    GRAY_B,
    QUERA_GREEN,
    QUERA_ORANGE,
    QUERA_RED,
    QUERA_YELLOW,
    CircuitDefinition,
    CircuitVisual,
    Create,
    ExplanationBox,
    LayerLabel,
)
from manimlib import *


def create_pulse_sequence_diagram():
    """Create a visual of the Levine-Pichler pulse sequence."""
    p1 = VGroup(
        Circle(radius=0.2, color=QUERA_RED, fill_opacity=0.3),
        Text("C", font_size=14, color=WHITE),
    )
    p1_label = Tex(r"\pi", font_size=11, color=QUERA_RED)
    p1_label.next_to(p1, DOWN, buff=0.1)

    p2 = VGroup(
        Circle(radius=0.25, color=QUERA_YELLOW, fill_opacity=0.3),
        Text("T", font_size=14, color=WHITE),
    )
    p2_label = Tex(r"2\pi", font_size=11, color=QUERA_YELLOW)
    p2_label.next_to(p2, DOWN, buff=0.1)

    p3 = VGroup(
        Circle(radius=0.2, color=QUERA_RED, fill_opacity=0.3),
        Text("C", font_size=14, color=WHITE),
    )
    p3_label = Tex(r"\pi", font_size=11, color=QUERA_RED)
    p3_label.next_to(p3, DOWN, buff=0.1)

    arrow1 = Arrow(LEFT * 0.2, RIGHT * 0.2, color=GRAY_B, stroke_width=2, buff=0)
    arrow2 = Arrow(LEFT * 0.2, RIGHT * 0.2, color=GRAY_B, stroke_width=2, buff=0)

    seq = VGroup(
        VGroup(p1, p1_label), arrow1, VGroup(p2, p2_label), arrow2, VGroup(p3, p3_label)
    )
    seq.arrange(RIGHT, buff=0.3)
    return seq


def show_decomposition_layer(scene: Scene, circuit: CircuitDefinition):
    """
    Animate Layer 2: Gate Decomposition.

    Args:
        scene: The Manim scene to animate in
        circuit: The circuit definition to visualize

    Returns:
        None (cleans up after itself)
    """
    label = LayerLabel(
        "Layer 2: Gate Decomposition", "Compile to Native Gates", color=QUERA_GREEN
    )
    label.to_corner(UL, buff=0.3)
    scene.play(FadeIn(label))

    explanation = ExplanationBox(
        "QuEra hardware cannot directly execute CNOT gates. "
        "The native two-qubit gate is CZ (controlled-Z), implemented via a Rydberg blockade. "
        "Every CNOT must be decomposed: CNOT = H . CZ . H",
        width=4,
        font_size=13,
        color=QUERA_GREEN,
    )
    explanation.to_corner(UP + RIGHT)
    scene.play(FadeIn(explanation))
    scene.wait(1.5)

    cnot_label = Text("CNOT", font_size=20, color=WHITE)
    equals = Text("=", font_size=24, color=WHITE)

    demo_circuit = CircuitDefinition(num_qubits=2)
    demo_circuit.h(1)
    demo_circuit.cz(0, 1)
    demo_circuit.h(1)

    circuit_vis = CircuitVisual(demo_circuit, wire_spacing=0.65)
    scene.play(Create(circuit_vis.wires), Write(circuit_vis.labels))
    for gate in demo_circuit.gates:
        circuit_vis.add_gate_visual(gate)

    scene.play(FadeIn(circuit_vis.gates))
    scene.wait(1)

    scene.play(FadeOut(explanation))

    lp_explanation = ExplanationBox(
        "One common CZ/controlled-phase implementation uses a Levine–Pichler–style blockade pulse sequence:\n"
        "1) Pi pulse excites Control to Rydberg state.\n"
        "2) 2Pi pulse on Target (blocked if Control is excited).\n"
        "3) Pi pulse de-excites Control.",
        width=4.5,
        font_size=12,
        color=QUERA_GREEN,
    )
    lp_explanation.to_edge(RIGHT, buff=0.3).shift(UP * 0.5)
    scene.play(FadeIn(lp_explanation))

    pulse_seq = create_pulse_sequence_diagram()
    pulse_seq.shift(DOWN * 1.5)
    scene.play(FadeIn(pulse_seq))

    pulses = [pulse_seq[0], pulse_seq[2], pulse_seq[4]]  # The circle groups
    pulse_labels = [
        r"\text{Control excited to }\ket{r}",
        r"\text{Target rotation (conditional; blocked by Rydberg if control is excited)}",
        r"\text{Control returns to ground}",
    ]

    for i, (pulse, plabel) in enumerate(zip(pulses, pulse_labels)):
        note = Tex(plabel, font_size=11, color=QUERA_YELLOW)
        note.next_to(pulse, DOWN, buff=0.5)
        scene.play(
            pulse[0].animate.set_fill(opacity=0.8).scale(1.2),
            FadeIn(note),
            run_time=0.5,
        )
        scene.wait(1.5)
        scene.play(
            pulse[0].animate.set_fill(opacity=0.3).scale(1 / 1.2),
            FadeOut(note),
            run_time=0.4,
        )

    cz_layers = circuit.get_cz_layers()
    num_cz = sum(len(layer) for layer in cz_layers)

    parallel_note = ExplanationBox(
        f"This circuit requires {num_cz} CZ gate{'' if num_cz == 1 else 's'}, grouped into {len(cz_layers)} parallel layers. "
        "Gates on disjoint qubits execute simultaneously, minimizing circuit depth.",
        width=4,
        font_size=12,
        color=QUERA_ORANGE,
    )
    parallel_note.to_edge(DOWN, buff=0.3)
    scene.play(FadeIn(parallel_note))
    scene.wait(1.5)

    all_elements = VGroup(label, lp_explanation, pulse_seq, parallel_note, circuit_vis)
    scene.play(FadeOut(all_elements))


class Layer2Demo(Scene):
    """Standalone demo of Layer 2."""

    def construct(self):
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        show_decomposition_layer(self, circuit)

"""
Layer 5: Hardware Execution

This layer shows the actual physical execution on Rubidium-87 atoms.
Qubits are individual atoms trapped in optical tweezers.

Key concepts visualized:
- Rubidium-87 atoms as qubits
- Hyperfine ground states |0> and |1>
- Rydberg excitation to |r>
- Blockade radius and interaction
- Fluorescence measurement
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from core import (
    QUERA_BLUE,
    QUERA_GREEN,
    QUERA_PURPLE,
    QUERA_RED,
    QUERA_YELLOW,
    AnimatedQubit,
    CircuitDefinition,
    Create,
    ExplanationBox,
    LayerLabel,
)
from manimlib import *


def show_hardware_layer(scene: Scene, circuit: CircuitDefinition):
    """
    Animate Layer 5: Hardware execution on Rydberg atoms.

    Args:
        scene: The Manim scene to animate in
        circuit: The circuit definition to visualize

    Returns:
        None (cleans up after itself)
    """
    label = LayerLabel(
        "Layer 5: Hardware Execution", "Rubidium-87 Atoms + Lasers", color=QUERA_PURPLE
    )
    label.to_corner(UL, buff=0.3)
    scene.play(FadeIn(label))

    physics_explanation = ExplanationBox(
        "Physical qubits are individual Rubidium-87 atoms trapped in optical tweezers. "
        "Qubit states |0> and |1> are encoded in hyperfine ground states "
        "with long coherence times.",
        width=4,
        font_size=12,
        color=QUERA_PURPLE,
    )
    physics_explanation.to_edge(RIGHT, buff=0.2).shift(UP * 1.5)
    scene.play(FadeIn(physics_explanation))

    num_q = circuit.num_qubits
    atoms = VGroup()
    atom_label_texts = VGroup()

    for i in range(num_q):
        x = (i - (num_q - 1) / 2) * 1.3
        atom = AnimatedQubit([x, 0, 0], radius=0.2, color=QUERA_PURPLE)
        atoms.add(atom)

        q_label = Text(f"q{i}", font_size=12, color=WHITE)
        q_label.next_to(atom, DOWN, buff=0.15)
        atom_label_texts.add(q_label)

    atoms_group = VGroup(atoms, atom_label_texts)
    scene.play(FadeIn(atoms_group))

    scene.play(FadeOut(physics_explanation))

    rydberg_explanation = ExplanationBox(
        "To create entanglement, atoms are excited to Rydberg states (e.g., 70S₁/₂) - "
        "highly excited states with enormous electron orbits. "
        "The strong dipole-dipole interaction creates a Rydberg blockade: "
        "if one atom is excited, nearby atoms cannot be excited simultaneously.",
        width=3.5,
        font_size=11,
        color=QUERA_PURPLE,
    )
    rydberg_explanation.to_edge(RIGHT, buff=0.2).shift(UP * 1.5)
    scene.play(FadeIn(rydberg_explanation))

    levels = VGroup(
        Line(LEFT * 0.4, RIGHT * 0.4, color=QUERA_BLUE),
        Line(LEFT * 0.4, RIGHT * 0.4, color=QUERA_GREEN).shift(UP * 0.5),
        Line(LEFT * 0.4, RIGHT * 0.4, color=QUERA_RED).shift(UP * 1.5),
    )
    level_labels = VGroup(
        Text("|0>", font_size=10, color=QUERA_BLUE),
        Text("|1>", font_size=10, color=QUERA_GREEN),
        Text("|r> Rydberg", font_size=10, color=QUERA_RED),
    )
    for lbl, level in zip(level_labels, levels):
        lbl.next_to(level, RIGHT, buff=0.1)

    energy_diagram = VGroup(levels, level_labels)
    energy_diagram.to_corner(DR, buff=0.5)
    scene.play(FadeIn(energy_diagram))

    excite_note = Text(
        "Exciting q0 to Rydberg state...", font_size=12, color=QUERA_YELLOW
    )
    excite_note.to_edge(DOWN, buff=0.5)
    scene.play(FadeIn(excite_note))

    scene.play(atoms[0].excite())

    blockade = Circle(
        radius=1.8, stroke_color=QUERA_RED, stroke_width=2, stroke_opacity=0.6
    )
    blockade.move_to(atoms[0].get_center())

    blockade_label = Text("Blockade radius (~3-6 μm)", font_size=10, color=QUERA_RED)
    blockade_label.next_to(blockade, UP, buff=0.1)

    scene.play(Create(blockade), FadeIn(blockade_label))

    if num_q > 1:
        blocked_note = Text("q1 BLOCKED from Rydberg!", font_size=11, color=QUERA_RED)
        blocked_note.next_to(atoms[1], UP, buff=0.2)
        scene.play(FadeIn(blocked_note))
        scene.wait(0.8)
        scene.play(FadeOut(blocked_note))

    scene.play(FadeOut(excite_note), FadeOut(blockade), FadeOut(blockade_label))
    scene.play(atoms[0].deexcite())

    scene.play(FadeOut(rydberg_explanation))

    result_explanation = ExplanationBox(
        "After the pulse sequence completes, the atoms are entangled! "
        "Measurement collapses the superposition to a classical bitstring.",
        width=3.5,
        font_size=11,
        color=QUERA_GREEN,
    )
    result_explanation.to_edge(RIGHT, buff=0.2).shift(UP * 1.5)
    scene.play(FadeIn(result_explanation))

    cz_layers = circuit.get_cz_layers()
    entangle_lines = VGroup()

    for layer in cz_layers:
        for gate in layer:
            q1, q2 = gate.qubits
            if q1 < len(atoms) and q2 < len(atoms):
                line = Line(
                    atoms[q1].get_center(),
                    atoms[q2].get_center(),
                    color=QUERA_GREEN,
                    stroke_width=3,
                )
                entangle_lines.add(line)

    scene.play(Create(entangle_lines))

    measure_note = Text("Measurement via fluorescence", font_size=12, color=QUERA_GREEN)
    measure_note.to_edge(DOWN, buff=0.5)
    scene.play(FadeIn(measure_note))

    for atom in atoms:
        scene.play(atom.pulse_once(run_time=0.3))

    scene.wait(1)

    all_elements = VGroup(
        label,
        atoms_group,
        energy_diagram,
        entangle_lines,
        result_explanation,
        measure_note,
    )
    scene.play(FadeOut(all_elements))


class Layer5Demo(Scene):
    """Standalone demo of Layer 5."""

    def construct(self):
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        show_hardware_layer(self, circuit)

"""
Layer 3: Spatial Routing

This layer bridges logical gates to physical locations on a neutral-atom chip.
We display the full logical circuit off to the side, then map each gate to a scheduled interaction event at a physical location.

Key concepts visualized:
- Logical-to-physical mapping for each gate
- Neutral-atom chip as a parallelogram surface
- Visual emphasis of gate location on the chip
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from core import (
    QUERA_BLUE,
    QUERA_GREEN,
    QUERA_ORANGE,
    QUERA_PURPLE,
    QUERA_RED,
    QUERA_YELLOW,
    AnimatedQubit,
    CircuitDefinition,
    CircuitVisual,
    Create,
    ExplanationBox,
    LayerLabel,
    ZoneBox,
)
from manimlib import *


def show_spatial_layer(scene: Scene, circuit: CircuitDefinition):
    """
    Animate Layer 3: Spatial Routing by mapping logical gates to chip locations.

    Args:
        scene: The Manim scene to animate in.
        circuit: The circuit definition to visualize.

    Returns:
        None (cleans up after itself).
    """
    label = LayerLabel(
        "Layer 3: Spatial Routing", "Logical → Physical Mapping", color=QUERA_YELLOW
    )
    label.to_corner(UL, buff=0.3)
    scene.play(FadeIn(label))

    explanation = ExplanationBox(
        "We now map each logical gate to a physical location on the neutral-atom chip. "
        "Unlike superconducting qubits, neutral atoms can be physically moved! "
        "The circuit is shown on the left; each gate is mapped onto the chip.",
        width=4.2,
        font_size=14,
        color=QUERA_YELLOW,
    )
    explanation.to_edge(UP, buff=0.7)
    scene.play(FadeIn(explanation))

    circuit_vis = CircuitVisual(circuit, wire_spacing=0.65)
    gate_visuals = []
    for gate in circuit.gates:
        gate_visuals.append(circuit_vis.add_gate_visual(gate))

    circuit_vis.scale(0.95)
    circuit_vis.move_to(LEFT * 2.6 + UP * 0.1)

    scene.play(FadeIn(circuit_vis))
    scene.wait(0.3)

    chip_origin = RIGHT * 1.4 + DOWN * 1.2
    chip_u = RIGHT * 5.2
    chip_v = UP * 2.5 + RIGHT * 1.0
    p0 = chip_origin
    p1 = chip_origin + chip_u
    p2 = chip_origin + chip_u + chip_v
    p3 = chip_origin + chip_v

    chip = Polygon(
        p0, p1, p2, p3, stroke_color=QUERA_BLUE, stroke_width=2, fill_opacity=0.12
    )
    chip.set_fill(QUERA_BLUE, opacity=0.12)
    chip_label = Text("Optical tweezer array region", font_size=16, color=QUERA_BLUE)
    chip_label.next_to(chip, UP, buff=0.1)

    def chip_point(u, v):
        return chip_origin + chip_u * u + chip_v * v

    num_q = circuit.num_qubits
    qubit_positions = []
    qubit_dots = VGroup()
    u_min, u_max = 0.12, 0.88
    for i in range(num_q):
        if num_q == 1:
            u = (u_min + u_max) / 2
        else:
            u = u_min + (u_max - u_min) * (i / (num_q - 1))
        v = 0.7 if i % 2 == 0 else 0.3
        pos = chip_point(u, v)
        qubit_positions.append(pos)
        qubit_dots.add(Dot(point=pos, radius=0.055, color=QUERA_PURPLE))

    scene.play(FadeIn(chip), FadeIn(chip_label), FadeIn(qubit_dots))

    def pulse_gate_location(gate):
        if gate.is_single_qubit:
            gate_pos = qubit_positions[gate.qubits[0]]
            ring_color = QUERA_PURPLE
        elif gate.is_two_qubit:
            q1, q2 = gate.qubits
            gate_pos = (qubit_positions[q1] + qubit_positions[q2]) / 2
            ring_color = QUERA_ORANGE
        else:
            return

        ring = Circle(radius=0.19, stroke_color=ring_color, stroke_width=3)
        ring.move_to(gate_pos)
        return ring, gate_pos

    for i, (gate, gate_vis) in enumerate(zip(circuit.gates, gate_visuals)):
        scene.play(gate_vis.animate.scale(1.08), run_time=0.12)
        scene.play(gate_vis.animate.scale(1 / 1.08), run_time=0.12)

        ring_result = pulse_gate_location(gate)
        if ring_result is not None:
            ring, gate_pos = ring_result
            arrow = Arrow(
                gate_vis.get_bottom(),
                gate_pos,
                stroke_color=QUERA_YELLOW,
                stroke_width=3,
                buff=0.1,
            )
            scene.play(Create(arrow), Create(ring), run_time=0.2)
            scene.play(
                ring.animate.scale(1.5).set_stroke(opacity=0),
                run_time=0.35,
                rate_func=there_and_back,
            )
            scene.remove(ring)
            scene.play(FadeOut(arrow), run_time=0.15)
    scene.wait(0.5)

    mapping_elements = VGroup(
        label,
        circuit_vis,
        chip,
        chip_label,
        qubit_dots,
        explanation,
    )
    scene.play(FadeOut(mapping_elements))
    scene.remove(mapping_elements)

    zone_explanation = ExplanationBox(
        "Optical tweezers physically transport atoms between dedicated zones: "
        "Storage (preserve coherence), Entangling (perform CZ gates), and Readout (measure).",
        width=4.2,
        font_size=13,
        color=QUERA_YELLOW,
    )
    zone_explanation.to_edge(UP, buff=0.7)
    scene.play(FadeIn(zone_explanation))

    storage_zone = ZoneBox(2, 2.2, "STORAGE ZONE", QUERA_BLUE)
    storage_desc = Text(
        "Qubits parked here\nLarge separation (>10 μm)\nNo interactions",
        font_size=11,
        color=QUERA_BLUE,
    )
    storage_desc.next_to(storage_zone.box, DOWN, buff=0.1)

    entangle_zone = ZoneBox(1.6, 1.6, "ENTANGLING ZONE", QUERA_RED)
    entangle_desc = Text(
        "Close proximity (~3-6 μm)\nRydberg blockade active\nCZ gates executed here",
        font_size=11,
        color=QUERA_RED,
    )
    entangle_desc.next_to(entangle_zone.box, DOWN, buff=0.1)

    readout_zone = ZoneBox(2, 2.2, "READOUT ZONE", QUERA_GREEN)
    readout_desc = Text(
        "Fluorescence measurement\nShielded region\nProtects other qubits",
        font_size=11,
        color=QUERA_GREEN,
    )
    readout_desc.next_to(readout_zone.box, DOWN, buff=0.1)

    storage_zone.shift(LEFT * 3 + DOWN * 1.6)
    storage_desc.shift(LEFT * 3 + DOWN * 1.6)
    entangle_zone.shift(DOWN * 1.6)
    entangle_desc.shift(DOWN * 1.6)
    readout_zone.shift(RIGHT * 3 + DOWN * 1.6)
    readout_desc.shift(RIGHT * 3 + DOWN * 1.6)

    zones = VGroup(
        storage_zone,
        storage_desc,
        entangle_zone,
        entangle_desc,
        readout_zone,
        readout_desc,
    )
    scene.play(FadeIn(zones))
    scene.wait(2.5)

    num_q = circuit.num_qubits
    atom_spacing = min(0.5, 1.8 / max(num_q, 1))
    atoms = VGroup()
    atom_labels = VGroup()

    for i in range(num_q):
        y_offset = (num_q - 1) / 2 - i
        pos = storage_zone.box.get_center() + UP * y_offset * atom_spacing
        atom = AnimatedQubit(pos, radius=0.12, color=QUERA_PURPLE)
        atoms.add(atom)
        lbl = Text(f"q{i}", font_size=12, color=WHITE)
        lbl.next_to(atom, RIGHT, buff=0.06)
        atom_labels.add(lbl)

    scene.play(FadeIn(atoms), FadeIn(atom_labels))

    scene.play(FadeOut(zone_explanation))
    tweezer_explanation = ExplanationBox(
        "Optical tweezers (focused laser beams) grab and move individual atoms. "
        "The bloqade-lanes compiler schedules MOVE instructions with safe, "
        "non-crossing trajectories to avoid collisions and heating.",
        width=4.2,
        font_size=12,
        color=QUERA_YELLOW,
    )
    tweezer_explanation.to_edge(UP, buff=0.7)
    scene.play(FadeIn(tweezer_explanation))

    tweezer = VGroup(
        Dot(radius=0.18, color=BLUE, fill_opacity=0.4),
        Circle(radius=0.24, stroke_color=BLUE, stroke_width=2),
    )
    tweezer.move_to(atoms[0].get_center())
    scene.play(FadeIn(tweezer))

    cz_layers = circuit.get_cz_layers()
    for layer_idx, layer in enumerate(cz_layers):
        layer_status = Text(
            f"CZ Layer {layer_idx + 1}/{len(cz_layers)}",
            font_size=16,
            color=QUERA_ORANGE,
        )
        layer_status.to_edge(DOWN, buff=0.5)
        scene.play(FadeIn(layer_status))

        animations = []
        for gate in layer:
            q1, q2 = gate.qubits
            target_y1 = entangle_zone.box.get_center()[1] + 0.2
            target_y2 = entangle_zone.box.get_center()[1] - 0.2
            target_x = entangle_zone.box.get_center()[0]

            animations.append(atoms[q1].animate.move_to([target_x, target_y1, 0]))
            animations.append(atoms[q2].animate.move_to([target_x, target_y2, 0]))
            animations.append(
                atom_labels[q1].animate.move_to([target_x + 0.2, target_y1, 0])
            )
            animations.append(
                atom_labels[q2].animate.move_to([target_x + 0.2, target_y2, 0])
            )

        animations.append(tweezer.animate.move_to(entangle_zone.box.get_center()))
        scene.play(*animations, run_time=0.8)

        for gate in layer:
            q1, q2 = gate.qubits
            interaction_line = Line(
                atoms[q1].get_center(),
                atoms[q2].get_center(),
                color=QUERA_RED,
                stroke_width=4,
            )
            interaction_glow = interaction_line.copy().set_stroke(width=10, opacity=0.3)

            cz_note = Text("CZ via Rydberg blockade", font_size=12, color=QUERA_RED)
            cz_note.next_to(entangle_zone.box, LEFT, buff=0.2)

            scene.play(
                Create(interaction_line),
                Create(interaction_glow),
                atoms[q1].pulse_once(run_time=0.5),
                atoms[q2].pulse_once(run_time=0.5),
                FadeIn(cz_note),
            )
            scene.play(
                FadeOut(interaction_line),
                FadeOut(interaction_glow),
                FadeOut(cz_note),
            )

        animations = []
        for i, atom in enumerate(atoms):
            y_offset = (num_q - 1) / 2 - i
            pos = storage_zone.box.get_center() + UP * y_offset * atom_spacing
            animations.append(atom.animate.move_to(pos))
            animations.append(atom_labels[i].animate.next_to(pos, RIGHT, buff=0.06))

        animations.append(tweezer.animate.move_to(storage_zone.box.get_center()))
        scene.play(*animations, run_time=0.5)
        scene.play(FadeOut(layer_status))

    readout_status = Text("Moving to Readout Zone", font_size=16, color=QUERA_GREEN)
    readout_status.to_edge(DOWN, buff=0.5)
    scene.play(FadeIn(readout_status))

    animations = []
    for i, atom in enumerate(atoms):
        y_offset = (num_q - 1) / 2 - i
        pos = readout_zone.box.get_center() + UP * y_offset * atom_spacing
        animations.append(atom.animate.move_to(pos))
        animations.append(atom_labels[i].animate.next_to(pos, RIGHT, buff=0.06))

    scene.play(*animations, FadeOut(tweezer), run_time=0.8)
    scene.play(FadeOut(readout_status))
    scene.wait(0.5)

    all_elements = VGroup(
        zones,
        atoms,
        atom_labels,
        tweezer_explanation,
    )
    scene.play(FadeOut(all_elements))


class Layer3Demo(Scene):
    """Standalone demo of Layer 3."""

    def construct(self):
        # Create a sample circuit
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        show_spatial_layer(self, circuit)

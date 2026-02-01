"""
QuEra Circuit Compilation Stack Animation - Main Entry Point

This is the main orchestrator that runs the complete animation through all layers.
Each layer is defined in its own file for collaborative editing.

Files:
- core.py: Shared components (CircuitDefinition, visual primitives)
- layer1_logical.py: Logical circuit representation
- layer2_decomposition.py: Gate decomposition to native gates
- layer3_spatial.py: Spatial routing with bloqade-lanes
- layer4_pulse.py: Pulse-level control with bloqade-analog
- layer5_hardware.py: Hardware execution on Rydberg atoms

Usage:
    manimgl main.py GHZCircuitDemo
    manimgl main.py BellStateDemo
    manimgl main.py FourQubitDemo
    manimgl main.py CustomCircuitDemo

    # Run individual layers for testing:
    manimgl layer1_logical.py Layer1Demo
    manimgl layer2_decomposition.py Layer2Demo
    # etc.
"""

import os
import sys

# why do i have to do this bruh
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from core import (
    GRAY_B,
    QUERA_BLUE,
    QUERA_GREEN,
    QUERA_PURPLE,
    QUERA_RED,
    QUERA_YELLOW,
    CircuitDefinition,
    GrowArrow,
)
from layer1_logical import show_logical_layer
from layer2_decomposition import show_decomposition_layer
from layer3_spatial import show_spatial_layer
from layer4_pulse import show_pulse_layer
from layer5_hardware import show_hardware_layer
from manimlib import *


class CompilationAnimation(Scene):
    """
    Base class for the complete compilation animation.

    Subclass this and override get_circuit() to animate your own circuit.
    """

    def get_circuit(self) -> CircuitDefinition:
        """Override this method to define your circuit."""
        raise NotImplementedError("Subclass must implement get_circuit()")

    def construct(self):
        """Run the complete animation pipeline."""
        self.circuit = self.get_circuit()

        self.show_title()

        show_logical_layer(self, self.circuit)
        show_decomposition_layer(self, self.circuit)
        show_spatial_layer(self, self.circuit)
        show_pulse_layer(self, self.circuit)
        show_hardware_layer(self, self.circuit)

        self.show_summary()

    def show_title(self):
        """Display the animation title."""
        title = Text("QuEra Compilation Pipeline", font_size=36, color=QUERA_PURPLE)
        circuit_name = Text(f"Circuit: {self.circuit.name}", font_size=24, color=WHITE)
        circuit_name.next_to(title, DOWN, buff=0.3)

        info = Text(
            f"{self.circuit.num_qubits} qubits | {len(self.circuit.gates)} gates",
            font_size=18,
            color=GRAY_B,
        )
        info.next_to(circuit_name, DOWN, buff=0.2)

        self.play(Write(title))
        self.play(FadeIn(circuit_name), FadeIn(info))
        self.wait(2.5)
        self.play(FadeOut(title), FadeOut(circuit_name), FadeOut(info))

    def show_summary(self):
        """Show the final compilation summary."""
        title = Text("Compilation Complete!", font_size=32, color=QUERA_PURPLE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        layers = VGroup()
        layer_data = [
            ("1. Logical Circuit", "Abstract gates & qubits", QUERA_BLUE),
            ("2. Gate Decomposition", "CNOT -> H-CZ-H", QUERA_GREEN),
            ("3. Spatial Routing", "Atom transport paths", QUERA_YELLOW),
            ("4. Pulse Control", "Laser waveforms", QUERA_RED),
            ("5. Hardware", "Rydberg atoms", QUERA_PURPLE),
        ]

        for name, desc, color in layer_data:
            box = VGroup(
                RoundedRectangle(
                    width=3.5,
                    height=0.6,
                    corner_radius=0.1,
                    fill_color=color,
                    fill_opacity=0.15,
                    stroke_color=color,
                    stroke_width=2,
                ),
                Text(name, font_size=14, color=color),
                Text(desc, font_size=10, color=GRAY_B),
            )
            box[1].move_to(box[0].get_center() + UP * 0.1)
            box[2].move_to(box[0].get_center() + DOWN * 0.12)
            layers.add(box)

        layers.arrange(DOWN, buff=0.15)
        layers.next_to(title, DOWN, buff=0.4)

        arrows = VGroup()
        for i in range(len(layers) - 1):
            arrow = Arrow(
                layers[i].get_bottom(),
                layers[i + 1].get_top(),
                buff=0.05,
                color=WHITE,
                stroke_width=2,
            )
            arrows.add(arrow)

        for layer, arrow in zip(layers[:-1], arrows):
            self.play(FadeIn(layer), run_time=0.3)
            self.play(GrowArrow(arrow), run_time=0.15)
        self.play(FadeIn(layers[-1]), run_time=0.3)

        cz_layers = self.circuit.get_cz_layers()
        stats = VGroup(
            Text(f"Circuit: {self.circuit.name}", font_size=16, color=WHITE),
            Text(
                f"Qubits: {self.circuit.num_qubits} | "
                f"Gates: {len(self.circuit.gates)} | "
                f"CZ Layers: {len(cz_layers)}",
                font_size=12,
                color=GRAY_B,
            ),
        ).arrange(DOWN, buff=0.1)
        stats.to_edge(DOWN, buff=0.5)

        self.play(FadeIn(stats))
        self.wait(2.5)

        final = Text("From Python to Photons", font_size=20, color=QUERA_PURPLE)
        final.next_to(stats, UP, buff=0.3)
        self.play(FadeIn(final))
        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects])


try:
    # ideally bloqade should be installed
    # but for testing i'm keeping this here
    from bloqade import squin

    BLOQADE_AVAILABLE = True

    @squin.kernel
    def ghz_kernel():
        """3-qubit GHZ state: |000> + |111>"""
        q = squin.qalloc(3)
        squin.h(q[0])
        squin.cx(q[0], q[1])
        squin.cx(q[1], q[2])

    @squin.kernel
    def bell_kernel():
        """2-qubit Bell state: |00> + |11>"""
        q = squin.qalloc(2)
        squin.h(q[0])
        squin.cx(q[0], q[1])

    @squin.kernel
    def four_qubit_star_kernel():
        """4-qubit star entanglement with q0 as hub"""
        q = squin.qalloc(4)
        squin.h(q[0])
        squin.cx(q[0], q[1])
        squin.cx(q[0], q[2])
        squin.cx(q[0], q[3])

    @squin.kernel
    def qft_style_kernel():
        """QFT-style circuit with CZ gates"""
        q = squin.qalloc(3)
        squin.h(q[0])
        squin.cz(q[0], q[1])
        squin.h(q[1])
        squin.cz(q[0], q[2])
        squin.cz(q[1], q[2])
        squin.h(q[2])

    @squin.kernel
    def custom_kernel():
        """Custom 5-qubit circuit with entangling layers"""
        q = squin.qalloc(5)
        for i in range(5):
            squin.h(q[i])
        squin.cx(q[0], q[1])
        squin.cx(q[2], q[3])
        squin.cx(q[1], q[2])
        squin.cx(q[3], q[4])
        squin.cz(q[0], q[2])
        squin.cz(q[1], q[3])

except ImportError:
    BLOQADE_AVAILABLE = False
    print("WARNING: Bloqade is not available!")


class GHZCircuitDemo(CompilationAnimation):
    """3-qubit GHZ state preparation using bloqade kernel."""

    def get_circuit(self) -> CircuitDefinition:
        if BLOQADE_AVAILABLE:
            return CircuitDefinition.from_bloqade(ghz_kernel, name="GHZ State")
        else:
            # fallback if bloqade not installed
            circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
            circuit.h(0).cx(0, 1).cx(1, 2).measure_all()
            return circuit


class BellStateDemo(CompilationAnimation):
    """2-qubit Bell state preparation using bloqade kernel."""

    def get_circuit(self) -> CircuitDefinition:
        if BLOQADE_AVAILABLE:
            return CircuitDefinition.from_bloqade(bell_kernel, name="Bell State")
        else:
            circuit = CircuitDefinition(num_qubits=2, name="Bell State")
            circuit.h(0).cx(0, 1).measure_all()
            return circuit


class FourQubitDemo(CompilationAnimation):
    """4-qubit star entanglement pattern using bloqade kernel."""

    def get_circuit(self) -> CircuitDefinition:
        if BLOQADE_AVAILABLE:
            return CircuitDefinition.from_bloqade(
                four_qubit_star_kernel, name="4-Qubit Star"
            )
        else:
            circuit = CircuitDefinition(num_qubits=4, name="4-Qubit Star")
            circuit.h(0).cx(0, 1).cx(0, 2).cx(0, 3).measure_all()
            return circuit


class CustomCircuitDemo(CompilationAnimation):
    """
    Template for custom circuits using bloqade kernel.

    Edit custom_kernel() above to create your own!"""

    def get_circuit(self) -> CircuitDefinition:
        if BLOQADE_AVAILABLE:
            return CircuitDefinition.from_bloqade(custom_kernel, name="Custom Circuit")
        else:
            circuit = CircuitDefinition(num_qubits=5, name="Custom Circuit")
            for i in range(5):
                circuit.h(i)
            circuit.cx(0, 1).cx(2, 3).cx(1, 2).cx(3, 4)
            circuit.cz(0, 2).cz(1, 3)
            circuit.measure_all()
            return circuit


if __name__ == "__main__":
    print("QuEra Circuit Compilation Animation")
    print("=" * 40)
    print()
    print("Available demos:")
    print("  manimgl main.py GHZCircuitDemo")
    print("  manimgl main.py BellStateDemo")
    print("  manimgl main.py FourQubitDemo")
    print("  manimgl main.py CustomCircuitDemo")
    print()
    print("Individual layer demos:")
    print("  manimgl layer1_logical.py Layer1Demo")
    print("  manimgl layer2_decomposition.py Layer2Demo")
    print("  manimgl layer3_spatial.py Layer3Demo")
    print("  manimgl layer4_pulse.py Layer4Demo")
    print("  manimgl layer5_hardware.py Layer5Demo")
    print()
    print("To create your own circuit:")
    print("  1. Edit CustomCircuitDemo.get_circuit() in main.py")
    print("  2. Or create a new class inheriting from CompilationAnimation")

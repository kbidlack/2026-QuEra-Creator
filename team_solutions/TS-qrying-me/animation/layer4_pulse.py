"""
Layer 4: Pulse Control

This layer shows the analog waveforms that drive the quantum operations.
The compiler generates precise time-dependent laser pulses.

Key concepts visualized:
- Time-dependent Hamiltonian H(t)
- Rabi frequency Omega(t) - laser intensity
- Detuning Delta(t) - laser frequency offset
- Blackman window pulse shapes
- bloqade-analog compiler
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import numpy as np
from core import (
    GRAY_B,
    QUERA_GREEN,
    QUERA_PURPLE,
    QUERA_RED,
    QUERA_YELLOW,
    CircuitDefinition,
    Create,
    ExplanationBox,
    LayerLabel,
)
from manimlib import *


def show_pulse_layer(scene: Scene, circuit: CircuitDefinition):
    """
    Animate Layer 4: Pulse-level control with bloqade-analog.

    Args:
        scene: The Manim scene to animate in
        circuit: The circuit definition to visualize

    Returns:
        None (cleans up after itself)
    """
    label = LayerLabel(
        "Layer 4: Pulse Control", "bloqade-analog - Waveforms", color=QUERA_RED
    )
    label.to_corner(UL, buff=0.3)
    scene.play(FadeIn(label))

    hamiltonian_explanation = ExplanationBox(
        "The compiler generates precise time-dependent laser pulses "
        "described by a Hamiltonian H(t). Three key terms control the quantum evolution "
        "of the neutral-atom system:",
        width=5,
        font_size=12,
        color=QUERA_RED,
    )
    hamiltonian_explanation.to_edge(UP, buff=0.7)
    scene.play(FadeIn(hamiltonian_explanation))

    hamiltonian = Tex(
        r"H(t)=\sum_i \frac{\hbar}{2}\Omega_i(t)\sigma_x^{(i)}"
        r"-\sum_i \hbar\Delta_i(t)n_i"
        r"+\sum_{i<j}V_{ij}n_in_j",
        font_size=26,
    )

    hamiltonian.next_to(hamiltonian_explanation, DOWN, buff=0.3)
    scene.play(Write(hamiltonian))

    terms = VGroup(
        Text(
            "Ω(t): Rabi frequency - drives rotations (laser intensity)",
            font_size=11,
            color=QUERA_YELLOW,
        ),
        Text(
            "Δ(t): Detuning - controls energy shifts (laser frequency)",
            font_size=11,
            color=QUERA_GREEN,
        ),
        Text(
            "V_ij ∝ 1/R⁶: Rydberg interaction - enables blockade",
            font_size=11,
            color=QUERA_PURPLE,
        ),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    terms.next_to(hamiltonian, DOWN, buff=0.3)

    for term in terms:
        scene.play(FadeIn(term), run_time=0.4)
    scene.wait(1)

    scene.play(FadeOut(hamiltonian_explanation), FadeOut(terms))

    waveform_explanation = ExplanationBox(
        "Entangling operations (CZ gates) are implemented with Rydberg blockade pulse sequences. "
        "Pulses use smooth shapes like Blackman windows to prevent "
        "errors from abrupt switching (adiabatic control). "
        "The pulse shape directly affects gate fidelity.",
        width=3.5,
        font_size=11,
        color=QUERA_RED,
    )
    waveform_explanation.to_edge(RIGHT, buff=0.2).shift(UP * 1)
    scene.play(FadeIn(waveform_explanation))

    axes_control = Axes(
        x_range=[0, 10, 2],
        y_range=[0, 1.2, 0.5],
        width=5.5,
        height=1.2,
        axis_config={"color": GRAY_B},
    )
    axes_target = Axes(
        x_range=[0, 10, 2],
        y_range=[0, 1.2, 0.5],
        width=5.5,
        height=1.2,
        axis_config={"color": GRAY_B},
    )

    axes_control.shift(UP * 0.3 + LEFT * 0.5)
    axes_target.shift(DOWN * 1.5 + LEFT * 0.5)

    control_label = Text("Control atom Ω(t)", font_size=11, color=QUERA_RED)
    control_label.next_to(axes_control, LEFT, buff=0.15)

    target_label = Text("Target atom Ω(t)", font_size=11, color=QUERA_YELLOW)
    target_label.next_to(axes_target, LEFT, buff=0.15)

    x_label = Text("Time (μs)", font_size=11, color=GRAY_B)
    x_label.next_to(axes_target, DOWN, buff=0.12)

    scene.play(
        Create(axes_control),
        Create(axes_target),
        FadeIn(control_label),
        FadeIn(target_label),
        FadeIn(x_label),
    )

    cz_layers = circuit.get_cz_layers()
    num_cz = max(len(cz_layers), 1)

    def blackman(t, t_start, t_end, amp=1.0):
        if t < t_start or t > t_end:
            return 0
        tau = (t - t_start) / (t_end - t_start)
        return amp * (0.42 - 0.5 * np.cos(2 * PI * tau) + 0.08 * np.cos(4 * PI * tau))

    pw = 8 / max(num_cz * 3, 3)  # Pulse width
    control_pulses = VGroup()
    target_pulses = VGroup()

    for i in range(num_cz):
        t_base = 1 + i * 3 * pw

        # Control atom: π pulse, gap, π pulse
        p1_ctrl = axes_control.get_graph(
            lambda t, tb=t_base: blackman(t, tb, tb + pw, 1.0), color=QUERA_RED
        )
        p3_ctrl = axes_control.get_graph(
            lambda t, tb=t_base: blackman(t, tb + 2 * pw, tb + 3 * pw, 1.0),
            color=QUERA_RED,
        )
        control_pulses.add(p1_ctrl, p3_ctrl)

        # Target atom: gap, 2π pulse, gap
        p2_tgt = axes_target.get_graph(
            lambda t, tb=t_base: blackman(t, tb + pw, tb + 2 * pw, 1.0),
            color=QUERA_YELLOW,
        )
        target_pulses.add(p2_tgt)

    pulse_legend = VGroup(
        Text("CZ gate sequence:", font_size=10, color=WHITE),
        Text("1. π pulse on Control", font_size=9, color=QUERA_RED),
        Text("2. 2π pulse on Target", font_size=9, color=QUERA_YELLOW),
        Text("3. π pulse on Control", font_size=9, color=QUERA_RED),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
    pulse_legend.next_to(axes_target, DOWN, buff=0.35)

    for i in range(num_cz):
        scene.play(Create(control_pulses[i * 2]), run_time=0.2)
        scene.play(Create(target_pulses[i]), run_time=0.2)
        scene.play(Create(control_pulses[i * 2 + 1]), run_time=0.2)

    scene.play(FadeIn(pulse_legend))

    sweep_ctrl = Line(
        axes_control.c2p(0, 0), axes_control.c2p(0, 1.2), color=WHITE, stroke_width=2
    )
    sweep_tgt = Line(
        axes_target.c2p(0, 0), axes_target.c2p(0, 1.2), color=WHITE, stroke_width=2
    )
    scene.play(
        sweep_ctrl.animate.move_to(axes_control.c2p(9, 0.6)),
        sweep_tgt.animate.move_to(axes_target.c2p(9, 0.6)),
        run_time=2,
    )

    scene.wait(1.5)

    all_elements = VGroup(
        label,
        hamiltonian,
        waveform_explanation,
        axes_control,
        axes_target,
        control_label,
        target_label,
        x_label,
        control_pulses,
        target_pulses,
        pulse_legend,
        sweep_ctrl,
        sweep_tgt,
    )
    scene.play(FadeOut(all_elements))


class Layer4Demo(Scene):
    """Standalone demo of Layer 4."""

    def construct(self):
        circuit = CircuitDefinition(num_qubits=3, name="GHZ State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        show_pulse_layer(self, circuit)

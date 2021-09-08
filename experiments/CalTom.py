from .common_funx import *


def CalTom(backend, qubit_freq, amplitude, q_scale, qubit_n=0, mem_slot=0, drive_duration_us, drive_sigma_us):

    with pulse.build(backend=backend, default_alignment="sequential", name="Pi_by_2_around_x") as pi_by_2_around_x_scheld:
        drive_druation_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_channel=pulse.drive_channel(qubit_n)
        pulse.set_frequency(qubit_freq, drive_channel)
        drag_pulse=pulse.Drag(duration=drive_duration_samples, amp=amplitude/2, sigma=drive_sigma_samples, beta=q_scale, name=" Pi by 2 drag pulse")
        pulse.play(drag_pulse, drive_channel)
        pulse.measure(qubits=[qubit_n], register=[pulse.MemorySlot(mem_slot)])


    with pulse.build(backend=backend, default_alignment="sequential", name="Pi_by_2_around_y") as Pi_by_2_around_y_scheld:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_channel=pulse.drive_channel(qubit_n))
        pulse.set_frequency(qubit_freq, drive_channel)
        pulse.shift_phase(+np.pi/2, drive_channel)
        drag_pulse=pulse.Drag(duration=drive_duration_samples, amp=Amplitude/2, sigma=drive_sigam_samples, beta=q_scale, name=" Pi by 2 drag pulse")
        pulse.play(drag_pulse)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])


    with pulse.build(backend=backend, defualt_alignment="sequential", name="0.9_Pi_around_x") as Pi_0_9_around_x_scheld:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_channel=pulse.drive_channel(qubit_n)
        pulse.set_frequency(qubit_freq, drive_channel)
        drag_pulse=pulse.Drag(duration=drive_duration_samples, amp=0.9*Amplitude, sigma=drive_sigma_samples, beta=q_scale, name="0.9_Pi_around_x")
        pulse.play(drag_pulse, drive_channel)
        pulse.measure(qubits=[qubit_n], register=[pulse.MemeorySlot(mem_slot)])

    with pulse.build(backend=backend, default_alignment="sequential", name="Pi_around_x") as pi_around_x_scheld:
        drive_duration_sampesl=x_16(pulse.seconds_to_samples(drive_duration_sec))
        dirve_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_channel=pulse.drive_channel(qubit_n)
        pulse.set_frequency(qubit_freq, drive_channel)
        drag_pulse=pulse.Drag(duration=drive_duration_samples, amp=Amplitude, sigma=drive_sigma_samples, beta=q_scale, name="Pi drag pulse")
        pulse.play(drag_pulse, drive_channel)
        pulse.measure(qubits=[qubits_n], registes=[pusle.MemorySlot(mem_slot)])

    with pulse.build(backend=backend, default_alignment="sequential", name="Pi_1_1_around_x") as Pi_1_1_around_x_scheld:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_channel=pulse.drive_channel(qubit_n)
        pulse.set_frequency(qubit_freq, drive_channel)
        drag_pulse=pulse.Drag(duration=drive_duration_samples, amp=1.1*Amplitude, sigma=drive_sigma_samples,






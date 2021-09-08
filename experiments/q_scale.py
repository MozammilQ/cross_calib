from .common_funx import *

def q_scale(backend, drive_duration_us, drive_sigma_us, precise_q_freq_Hz, amplitude, mean_gnd, mean_exc, qubit_n=0, mem_slot=0, num_of_experiments=60, q_s_min=-1.5, q_s_max=+1.5, num_of_shots_per_point=1024):

    with pulse.build(backend=backend, default_alignment='sequential', name="Drag_Pulse") as drag_pulse_x:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drag_pi_by_2_pls=pulse.Drag(drive_duration_samples, Amplitude/2, drive_sigma_samples, q_s, name="QScale Calibration")
        drag_pi_pulse=pulse.Drag(drive_duration_samples, Amplitude, drive_sigma_samples, q_s, name="Qscale Calibration")
        drive_chanl=pulse.drive_channel(qubit_n)
        pulse.set_frequency(precise_q_freq_Hz, drive_chanl)
        pulse.play(drag_pi_by_2_pls, drive_chanl)
        pulse.play(drag_pi_pulse, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])


    with pulse.build(backend=backend, default_alignment='sequential', name="Drag_Pulse") as drag_pulse_neg_y:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drag_pi_by_2_pls=pulse.Drag(drive_duration_samples, Amplitude/2, drive_sigma_samples, q_s, name="QScale Calibration")
        drag_pi_pulse=pulse.Drag(drive_duration_samples, Amplitude, drive_sigma_samples, q_s, name="Qscale Calibration")
        drive_chanl=pulse.drive_channel(qubit_n)
        pulse.set_frequency(precise_q_freq_Hz, drive_chanl)
        pulse.play(drag_pi_by_2_pls, drive_chanl)
        pulse.shift_phase(-np.pi/2, drive_chanl)
        pulse.play(drag_pi_pulse, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])


    with pulse.build(backend=backend, default_alignment='sequential', name="Drag_Pulse") as drag_pulse_y:
        drive_duration_samples=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma_samples=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drag_pi_by_2_pls=pulse.Drag(drive_duration_samples, Amplitude/2, drive_sigma_samples, q_s, name="QScale Calibration")
        drag_pi_pulse=pulse.Drag(drive_duration_samples, Amplitude, drive_sigma_samples, q_s, name="Qscale Calibration")
        drive_chanl=pulse.drive_channel(qubit_n)
        pulse.set_frequency(precise_q_freq_Hz, drive_chanl)
        pulse.play(drag_pi_by_2_pls, drive_chanl)
        pulse.shift_phase(+np.pi/2, drive_chanl)
        pulse.play(drag_pi_pulse, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])


    q_s_range=np.linspace(-1.5,1.5,num_of_experiments)
    schedules_x=[drag_pulse_x.assign_parameters({q_s: qscale}, inplace=False) for qscale in q_s_range]
    schedules_neg_y=[drag_pulse_neg_y.assign_parameters({q_s: qscale}, inplace=False) for qscale in q_s_range]
    schedules_y=[drag_pulse_y.assign_parameters({q_s: qscale}, inplace=False) for qscale in q_s_range]

    job_x=backend.run(schedules_x, meas_level=1, meas_return='single', shots=num_of_shots_per_point)
    job_x.wait_for_final_state(timeout=None, wait=30, callback=None)
    result_shed_x=job_x.result(timeout=120)

    job_neg_y=backend.run(schedules_neg_y, meas_level=1, meas_return='single', shots=num_of_shots_per_point)
    job_neg_y.wait_for_final_state(timeout=None, wait=30, callback=None)
    result_shed_neg_y=job_neg_y.result(timeout=120)

    job_y=backend.run(schedules_y, meas_level=1, meas_return='single', shots=num_of_shots_per_point)
    job_y.wait_for_final_state()
    result_shed_y=job_y.result(timeout=120)


    import math

    def classify(point: complex):
        """Classify the given state as |0> or |1>."""
        def distance(a, b):
            return math.sqrt((np.real(a) - np.real(b))**2 + (np.imag(a) - np.imag(b))**2)
        return int(distance(point, mean_exc) < distance(point, mean_gnd))

    _x_val=[]
    for i in range(len(q_s_range)):
        iq_data=result_shed_x.get_memory(i)[:,qubit_n]*scale_fact
        _x_val.append(sum(map(classify, iq_data))/num_of_shots_per_point)

    neg_y_val=[]
    for i in range(len(q_s_range)):
        iq_data=result_shed_neg_y.get_memory(i)[:,qubit_n]*scale_fact
        neg_y_val.append(sum(map(classify, iq_data))/num_of_shots_per_point)

    _y_val=[]
    for i in range(len(q_s_range)):
        iq_data=result_shed_y.get_memory(i)[:, qubit_n]*scale_fact
        _y_val.append(sum(map(classify, iq_data))/num_of_shots_per_point)

    fit_data_fnx=lambda q_s_, m, c: (m*q_s_)+c
    init_param_y=[]
    m_and_c_y, conv=curve_fit(fit_data_fnx, q_s_range, _x_val)


    init_param_neg_y=[]
    m_and_c_neg_y, conv=curve_fit( fit_data_fnx, q_s_range, neg_y_val)

    q_scale,_=np.linalg.solve( [[m_and_c_y[0], -1], [m_and_c_neg_y[0], -1]], [-m_and_c_y[1], -m_and_c_neg_y[1]] )

    return q_scale


from .common_funx import *
from experiments.pulse_collection import X90_Pulse, Pi_Pulse

def T2(backend, mean_gnd, mean_exc, precise_q_freq_Hz, pi_ampl, qubit_n=0, drive_sigma_us=0.075, mem_slot=0, tau_max_us=200, tau_step_us=4, shots_per_point=512):
    tau_max_sec=tau_max_us*us
    tau_step_sec=tau_step_us*us
    delay_times_sec = np.arange(2*us, tau_max_sec, tau_step_sec)
    x90_pls=X90_Pulse(backend=backend, drive_ampl=pi_ampl/2, qubit_n=0, drive_sigma_us=0.075, pulse_name="x90_pulse")
    pi_pls=Pi_Pulse(backend=backend, pi_ampl=pi_ampl, qubit_n=0, drive_sigma_us=0.075, pulse_name="pi_pulse")

    t2_schedules = []
    for delay in delay_times_sec:
        with pulse.build(backend=backend, default_alignment='sequential', name=f"T2 delay = {delay / ns} ns") as t2_schedule:
            drive_chanl=pulse.drive_channel(qubit_n)
            pulse.set_frequency(precise_q_freq_Hz, drive_chanl)
            pulse.call(x90_pls)
            pulse.delay(x_16(pulse.seconds_to_samples(delay)), drive_chanl)
            pulse.call(pi_pls)
            pulse.delay(x_16(pulse.seconds_to_samples(delay)), drive_chanl)
            pulse.call(x90_pls)
            pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])
        t2_schedules.append(t2_schedule)

    job=backend.run(t2_schedules, meas_level=1, meas_return='single', shots=shots_per_point)

    print("\nJob submitted waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    def classify(point: complex):
        def distance(a, b):
            return math.sqrt((np.real(a) - np.real(b))**2 + (np.imag(a) - np.imag(b))**2)
        return int(distance(point, mean_exc) < distance(point, mean_gnd))


    if(stats.name=="DONE"):
        t2_results=job.result(timeout=120)
        t2_val = []

        for i in range(len(delay_times_sec)):
            iq_data = t2_results.get_memory(i)[:,qubit_n] * scale_fact
            t2_val.append(sum(map(classify, iq_data))/shots_per_point)

        data_fnx=lambda x, A, B, T2: (A * np.exp(-x / T2) + B)
        init_param=[-3, 0, 100]
        fit_params, y_fit = fit_fnx(2*delay_times_sec/us, t2_val, data_fnx, init_param)
        _, _, T2 = fit_params
        return T2
    else:
        print(stats.value)
        print(job.error_message())





from .common_funx import *

def ramsey_experiment(backend, pi_ampl, rough_q_freq_Hz, mean_gnd, mean_exc, qubit_n=0, mem_slot=0, time_max_us=1.8, time_step_us=0.025, drive_sigma_us=0.075, wait_time=45, num_shots=256):
    time_max_sec=time_max_us*us
    time_step_sec=time_step_us*us
    drive_ampl=pi_ampl/2

    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    delay_times_sec = np.arange(0.1*us, time_max_sec, time_step_sec)

    with pulse.build(backend) as x90_pulse:
        drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma=pulse.seconds_to_samples(drive_sigma_sec)
        drive_chanl=pulse.drive_channel(qubit_n)
        gauss_pulse=pulse.Gaussian(duration=drive_duration, amp=drive_ampl, sigma=drive_sigma, name='x90_pulse')
        pulse.play(gauss_pulse, drive_chanl)

    detuning_MHz=2
    ramsey_frequency=round(rough_q_freq_Hz+detuning_MHz*MHz, 6)

    ramsey_schedules = []
    for delay in delay_times_sec:
        with pulse.build(backend=backend, default_alignment='sequential', name=f"Ramsey delay = {delay / ns} ns") as ramsey_schedule:
            drive_chanl=pulse.drive_channel(qubit_n)
            pulse.set_frequency(ramsey_frequency, drive_chanl)
            pulse.call(x90_pulse)
            pulse.delay(x_16(pulse.seconds_to_samples(delay)), drive_chanl)
            pulse.call(x90_pulse)
            pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

        ramsey_schedules.append(ramsey_schedule)

    job = backend.run(ramsey_schedules, meas_level=1, meas_return='single', shots=num_shots)
    print("\nJob submitted waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    def classify(point: complex):
        def distance(a, b):
            return math.sqrt((np.real(a) - np.real(b))**2 + (np.imag(a) - np.imag(b))**2)
        return int(distance(point, mean_exc) < distance(point, mean_gnd))


    if(stats.name=="DONE"):
        ramsey_results = job.result(timeout=120)
        ramsey_values = []

        for i in range(len(delay_times_sec)):
            iq_data = ramsey_results.get_memory(i)[:,qubit_n] * scale_fact
            ramsey_values.append(sum(map(classify, iq_data)) / num_shots)

        init_param=[5, 1./0.4, 0, 0.25]
        data_fnx=lambda x, A, del_f_MHz, C, B: (A*np.cos(2*np.pi*del_f_MHz*x-C)+B)
        fit_params, y_fit=fit_fnx(delay_times_sec/us, np.real(ramsey_values), data_fnx, init_param)
        _, del_f_MHz, _, _, = fit_params
        precise_q_freq_Hz=rough_q_freq_Hz+(del_f_MHz-detuning_MHz)*MHz
        return precise_q_freq_Hz
    else:
        print(stats.value)
        print(job.error_message())



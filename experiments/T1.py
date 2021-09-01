from .common_funx import *

def T1(backend, pi_ampl, rough_q_freq_Hz, mean_gnd, mean_exc, qubit_n=0, mem_slot=0, drive_sigma_us=0.075, time_max_us=450, time_step_us=6.5, num_shots=256):
    time_max_sec=time_max_us*us
    time_step_sec=time_step_us*us
    delay_times_sec = np.arange(1*us, time_max_sec, time_step_sec)

    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    with pulse.build(backend) as pi_pulse:
        drive_duration = x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma = pulse.seconds_to_samples(drive_sigma_sec)
        drive_chanl = pulse.drive_channel(qubit_n)
        gussn=pulse.Gaussian(duration=drive_duration, amp=pi_ampl, sigma=drive_sigma, name="pi_pulse")
        pulse.play(gussn, drive_chanl)

    t1_schelds = []
    for delay in delay_times_sec:
        with pulse.build(backend=backend, default_alignment='sequential', name=f"T1 delay = {delay / ns} ns") as t1_schedule:
            drive_chanl = pulse.drive_channel(qubit_n)
            pulse.set_frequency(rough_q_freq_Hz, drive_chanl)
            pulse.call(pi_pulse)
            pulse.delay(x_16(pulse.seconds_to_samples(delay)), drive_chanl)
            pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])
        t1_schelds.append(t1_schedule)

    job = backend.run(t1_schelds, meas_level=1, meas_return='single', shots=num_shots)
    
    print("\nJob submitted waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    def classify(point: complex):
        def distance(a, b):
            return math.sqrt((np.real(a) - np.real(b))**2 + (np.imag(a) - np.imag(b))**2)
        return int(distance(point, mean_exc) < distance(point, mean_gnd))

    if(stats.name=="DONE"):
        t1_results=job.result(timeout=120)
        t1_val=[]

        for i in range(len(delay_times_sec)):
            iq_data = t1_results.get_memory(i)[:,qubit_n] * scale_fact
            t1_val.append(sum(map(classify, iq_data))/num_shots)

        init_param=[-3, 3, 100]
        data_fnx=lambda x, A, C, T1: (A * np.exp(-x / T1) + C)
        fit_params, y_fit=fit_fnx(delay_times_sec/us, t1_val, data_fnx, init_param)
        _, _, T1=fit_params
        return T1
    else:
        print(stats.value)
        print(job.error_message())




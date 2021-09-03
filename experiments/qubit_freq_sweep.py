from .common_funx import *

def qubit_freq_sweep(backend, qubit_n=0, mem_slot=0, freq_span_MHz=30, freq_step_MHz=0.5, drive_sigma_us=0.075, drive_ampl=0.05, shots_per_freq=1024, wait_time=45):
    backend_defaults=backend.defaults()
    freq_span_Hz=freq_span_MHz*MHz
    freq_step_Hz=freq_step_MHz*MHz

    center_freq_Hz=backend_defaults.qubit_freq_est[qubit_n]

    freq_span_min_Hz=center_freq_Hz - (freq_span_Hz/2)

    freq_span_max_Hz=center_freq_Hz + (freq_span_Hz/2)
    freq_sweep_Hz=np.arange(freq_span_min_Hz, freq_span_max_Hz, freq_step_Hz)

    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    freq=Parameter('freq')
    with pulse.build(backend=backend, default_alignment='sequential', name='Qubit Freq Sweep') as sweep_sched:
        drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma=pulse.seconds_to_samples(drive_sigma_sec)
        drive_chanl=pulse.drive_channel(qubit_n)
        pulse.set_frequency(freq, drive_chanl)
        gauss_pulse=pulse.Gaussian(duration=drive_duration, sigma=drive_sigma, amp=drive_ampl, name='freq_swp_excit_pulse')
        pulse.play(gauss_pulse, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

    pulse_schelds=[sweep_sched.assign_parameters({freq: f}, inplace=False) for f in freq_sweep_Hz]
    job=backend.run(pulse_schelds, meas_level=1, meas_return='avg', shots=shots_per_freq)

    print("\nJob submitted for Frequency Sweep Experiment waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    if(stats.name=="DONE"):
        freq_swp_res=job.result(timeout=120)
        sweep_val=[]
        for i in range(len(freq_swp_res.results)):
            res=freq_swp_res.get_memory(i)*scale_fact
            sweep_val.append(res[qubit_n])

        init_param=[5, 4.975, 1, -15]
        data_fnx=lambda x, A, q_freq, B, C : ( A / np.pi ) * (B / (x-q_freq)**2 + B**2) + C
        fit_params, y_fit=fit_fnx(freq_sweep_Hz/GHz, np.real(sweep_val), data_fnx, init_param)
        A, rough_q_freq, B, C=fit_params
        rough_q_freq_Hz=rough_q_freq*GHz
        return int(rough_q_freq_Hz)
    else:
        print(f"Job status is -->> {stats.value}")
        print(job.error_message())




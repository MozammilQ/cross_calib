from .common_funx import *

def remove_baseline(values):
    return np.array(values) - np.mean(values)

def rabi_measurment(backend, rough_q_freq_Hz, qubit_n=0, mem_slot=0, rabi_points=50, drive_ampl_min=0, drive_ampl_max=0.75, drive_sigma_us=0.075,  shots_per_point=1024):
    drive_ampls=np.linspace(drive_ampl_min, drive_ampl_max, rabi_points)
    drive_ampl=Parameter('drive_amp')
    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8
    with pulse.build(backend=backend, default_alignment='sequential', name='Rabi Measurment') as rabi_sched:
        drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma=x_16(pulse.seconds_to_samples(drive_sigma_sec))
        drive_chanl=pulse.drive_channel(qubit_n)
        pulse.set_frequency(rough_q_freq_Hz, drive_chanl)
        gauss_pulse=pulse.Gaussian(duration=drive_duration, amp=drive_ampl, sigma=drive_sigma, name="Rabi Pulse")
        pulse.play(gauss_pulse, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

    rabi_schedl=[rabi_sched.assign_parameters({drive_ampl: a}, inplace=False) for a in drive_ampls]

    job=backend.run(rabi_schedl, meas_level=1, meas_return='avg', shots=shots_per_point)
    
    print("\nJob submitted waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    if(stats.name=="DONE"):
        rabi_results=job.result(timeout=120)
        rabi_val=[]
        for i in range(rabi_points):
            rabi_val.append(rabi_results.get_memory(i)[qubit_n]*scale_factor)

        rabi_val=np.real(remove_baseline(rabi_val))

        rabi_init_param=[3, 0.1, 0.3, 0]
        rabi_fnx=lambda x, A, B, drive_period, phi: (A*np.cos(2*np.pi*x/drive_period - phi)+B)
        fit_params, y_fit=fit_fnx(drive_ampl, rabi_val, rabi_fnx, rabi_init_param)
        drive_period=fit_params[2]
        pi_ampl=abs(drive_period/2)
        return pi_ampl
    else:
        print(stats.value)
        print(job.error_message())






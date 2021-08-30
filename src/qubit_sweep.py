import numpy as np
from qiskit import pulse
from qiskit.circuit import Parameter
import time
from scipy.optimize import curve_fit

class qubit_freq_sweep:
    def __init__(self):
        self.KHz=1.0E+3
        self.MHz=1.0E+6
        self.GHz=1.0E+9
        self.us=1.0E-6
        self.ns=1.0E-9
        self.qubit_n=0
        self.mem_slot=0
        self.drive_ampl=0.05
        self.scale_fact=1.0E-14
        self.sht_per_freq=1024
        self.wait_time=120

    def x_16(x):
        return int(x+8)-int((x+8)%16)

    def fit_fnx(x_val, y_val, fnx, init_params):
        fit_params, conv=curve_fit(fnx, x_val, y_val, init_params)
        y_fit=fnx(x_val, *fit_params)
        return fit_params, y_fit

    def qubit_freq_sweep(backend):
        backend_defaults=backend.defaults()
        
        freq_span_Hz=30*MHz
        freq_step_Hz=0.5*MHz

        center_freq_Hz=backend_defaults.qubit_est_freq[qubit_n]
        freq_span_min_Hz=center_freq_Hz - (freq_span_Hz/2)
        freq_span_max_Hz=center_freq_Hz + (freq_span_Hz/2)

        freq_sweep_Hz=np.arange(freq_span_min_Hz, freq_span_max_Hz, freq_step_Hz)

        drive_sigma_sec=0.075*us
        driver_duration_sec=drive_sigma_sec*8

        freq=Parameter('freq')
        with pulse.build(backend=backend, default_alignment='sequential', name='Qubit Freq Sweep') as sweep_sched:
            drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
            driver_sigma=pulse.seconds_to_samples(drive_sigma_sec)
            drive_chanl=pulse.drive_channel(qubit_n)
            pulse.set_frequency(freq, drive_chanl)
            guass_pulse=pulse.Gaussian(duration=drive_duration, sigma=drive_sigma, amp=drive_ampl, name='freq_swp_excit_pulse')

            pulse.play(gauss_pulse, drive_chanl)
            pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

        pulse_schelds=[sweep_sched.assign_parameters({freq: f}, inplace=False) for f in freq_sweep_Hz]
        job=backend.run(pulse_schelds, meas_level=1, meas_return='avg', shots=sht_per_freq)

        var=job.status()
        while(var.name!='DONE'):
            sleep(wait_time)
            print("From qubit_freq_sweep -->  ")
            println(var.value)
            var=job.status()

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
        print(rough_q_freq_Hz)


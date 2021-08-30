import numpy as np
from qiskit import pulse
from qiskit.circuit import Parameter
import time
from scipy.optimize import curve_fit

class rabi_measurment:
    def __init__(self):
        self.KHz=1.0E+3
        self.MHz=1.0E+6
        self.GHz=1.0E+9
        self.us=1.0E-6
        self.ns=1.0E-9
        self.scale_fact=1.0E-14
        self.wait_time=120

    def x_16(x):
        return int(x+8)-int((x+8)%16)

    def fit_fnx(x_val, y_val, fnx, init_params):
        fit_params, conv=curve_fit(fnx, x_val, y_val, init_params)
        y_fit=fnx(x_val, *fit_params)
        return fit_params, y_fit

    def rabi_measurment(backend, rough_q_freq_Hz, qubit_n=0, mem_slot=0, rabi_points=50, drive_ampl_min=0, drive_ampl_max=0.75, drive_sigma_us=0.75, shots_per_point=1024):
        rabi_points=50
        drive_ampl_min=0
        drive_ampl_max=0.75
        drive_ampls=np.linspace(drive_ampl_min, drive_ampl_max, rabi_points)
        drive_ampl=Parameter('drive_amp')
        drive_sigma_sec=drive_sigma_us*us
        drive_duration_sec=drive_sigma_sec*8
        with pulse.build(backend=backend, default_alignment='sequential', name='Rabi Measurment') as rabi_sched:
            drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
            drive_sigma=x_16(pulse.seconds_to_samples(drive_sigma_sec))
            drive_chanl=pulse.drive_channel(qubit_n)
            gauss_pulse=pulse.Gaussian(duration=drive_duration, amp=drive_ampl, sigma=drive_sigma, name="Rabi Pulse")
            pulse.play(gauss_pulse, drive_chanl)
            pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])
            rabi_schedl=[rabi_sched.assign_parameters({drive_ampl: a}, inplace=False) for a in drive_ampls]

        job=backend.run(rabi_schedl, meas_level=1, meas_return='avg', shots=shots_per_point)

        stats=job.status()
        while(stats.name!='DONE'):
            print("From Rabi Measurment")
            println(stats.value)
            time.sleep(wait_time)
            stats=job.status()

        rabi_results=job.results(timeout=120)
        rabi_val=[]

        for i in range(rabi_points):
            rabi_val.append(rabi_results.get_memory(i)[qubit_n]*scale_factor)
        
        rabi_val=np.real(remove_baseline(rabi_val))
        rabi_init_param=[3, 0.1, 0.3, 0]
        rabi_fnx=lambda x, A, B, drive_period, phi: (A*np.cos(2*np.pi*x/drive_period - phi)+B)
        fit_params, y_fit=fit_function(drive_ampl, rabi_val, rabi_fnx, rabi_init_param)
        drive_period=fit_params[2]
        pi_ampl=abs(drive_period/2)
        print(f"Pi Amplitude is --> {pi_ampl}")



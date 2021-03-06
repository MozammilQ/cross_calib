from .common_funx import *
from experiments.pulse_collection import Pi_Pulse

def test_funx(backend, pi_ampl, rough_q_freq_Hz, qubit_n=0, mem_slot=0, drive_sigma_us=0.075, shots_per_freq=1024):
    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    pi_pls=Pi_Pulse(backend=backend, pi_ampl=pi_ampl, qubit_n=0, drive_sigma_us=0.075, pulse_name="pi_pulse")

    with pulse.build(backend=backend, default_alignment='sequential', name='ground state') as gnd_schedule:
        drive_chanl = pulse.drive_channel(qubit_n)
        pulse.set_frequency(rough_q_freq_Hz, drive_chanl)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

    with pulse.build(backend=backend, default_alignment='sequential', name='excited state') as exc_schedule:
        drive_chanl = pulse.drive_channel(qubit_n)
        pulse.set_frequency(rough_q_freq_Hz, drive_chanl)
        pulse.call(pi_pls)
        pulse.measure(qubits=[qubit_n], registers=[pulse.MemorySlot(mem_slot)])

    job = backend.run([gnd_schedule, exc_schedule], meas_level=1, meas_return='single', shots=shots_per_freq)
    
    print("\nJob submitted for test_funx waiting for completion\n")
    job.wait_for_final_state(timeout=None, wait=wait_time, callback=None)
    time.sleep(5)
    stats=job.status()

    if(stats.name=="DONE"):
        gnd_exc_results=job.result(timeout=120)
        gnd_results=gnd_exc_results.get_memory(0)[:, qubit_n]*scale_fact
        exc_results=gnd_exc_results.get_memory(1)[:, qubit_n]*scale_fact
        mean_gnd=np.mean(gnd_results)
        mean_exc=np.mean(exc_results)
        return mean_gnd, mean_exc
    else:
        print(stats.value)
        print(job.error_message())



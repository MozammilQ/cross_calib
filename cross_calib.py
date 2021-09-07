import csv
data_log_file="calibration_parameters_log.csv"
fields=["Time_Stamp", "Qubit_Number", "Qubit Freq (Freq Sweep)", "Loop number", "Pi Amplitude", "mean_gnd","mean_exc", "Precise Qubit Freq (Hz)"]
row=[]
csv_file=open(data_log_file,'r+')
csvwriter=csv.writer(csv_file)
csvwrite.writerow(fields)


###  Armonk has one qubit
qubits_to_calibrate=1


###  Number of times of calibration loop
num_loop=1



drive_sigma_us=0.075
freq_span_MHz=30
freq_step_MHz=0.5
test_drive_ampl=0.05



####   Get the backend
from qiskit import IBMQ
#IBMQ.save_account("id")
IBMQ.load_account()
provider=IBMQ.get_provider(hub="ibm-q", group="open", project="main")
backend=provider.get_backend("ibmq_armonk")


'''
Check if number of qubits to calibrate are less 
than the actual number of qubits on system
'''

import time
from experiments.qubit_freq_sweep import qubit_freq_sweep
from experiments.rabi_experiment import rabi_experiment
from experiments.ramsey_experiment import ramsey_experiment
from experiments.pulse_collection import X90_Pulse, Pi_Pulse
from experiments.test_funx import test_funx

list_of_qubits=range(1,num_of_qubits)

for qubit in list_of_qubits:

    ### Get Time Stamp into the CSV
    current_time=time.ctime() + " " + time.tzname[1]
    row.append(current_time)


    #Write qubit number which is getting calibrated now
    row.append(str(qubit))

    #Get rough estimate for qubit frequency with Frequency sweep method
    qubit_freq=qubit_freq_sweep(backend, qubit_n=qubit, mem_slot=0, freq_span_MHz=freq_span_MHz,\
            freq_step_MHz=freq_step_MHz, drive_sigma_us=drive_sigma_us, drive_ampl=test_drive_ampl, shots_per_freq=1024, wait_time=45)

    # Write the rough qubit frequency estimate in the CSV File
    row.append(str(qubit_freq))

    for loop in range(1,num_loop+1):

        #Write loop number in CSV
        row.append(str(loop))


        ### Rabi - Experiment Number: 1
        ###############################################################################################

        #Call Rabi
        pi_amplitude=rabi_experiment(backend=backend, rough_q_freq_Hz=qubit_freq, qubit_n=qubit, \
                mem_slot=0, rabi_points=50, drive_ampl_min=0, drive_ampl_max=0.75, \
                drive_sigma_us=drive_sigma_us,  shots_per_point=1024)
        #Update the Pi Amplitude in CSV file
        rows.append(str(pi_amplitude))
        ###############################################################################################




        ### Ramsey - Experiment Number: 2
        ###############################################################################################

        ### Get mean_gnd, mean_exc
        mean_gnd, mean_exc=test_funx(backend=backend, pi_ampl=pi_amplitude, rough_q_freq_Hz=qubit_freq, qubit_n=qubit, \
                mem_slot=0, drive_sigma_us=drive_sigma_us, shots_per_freq=1024)
        ### Write mean_gnd, mean_exc values in CSV
        row.append(str(mean_gnd)+" "+str(mean_exc))

        precise_q_freq_Hz=ramsey_experiment(backend=backend, pi_ampl=pi_amplitude, rough_q_freq_Hz=qubit_freq, \
                mean_gnd=mean_gnd, mean_exc=mean_exc, qubit_n=qubit, mem_slot=0, time_max_us=1.8, \
                time_step_us=0.025, drive_sigma_us=0.075, wait_time=45, num_shots=256)

        ### Write precise frequency determined by Ramsey Experiment in the CSV File
        row.append(str(precise_q_freq_Hz))
        ###############################################################################################




        ###  Rabi - Experiment Number: 3
        ###############################################################################################

        #Call Rabi
        pi_amplitude=rabi_experiment(backend=backend, rough_q_freq_Hz=qubit_freq, qubit_n=qubit, \
                mem_slot=0, rabi_points=50, drive_ampl_min=0, drive_ampl_max=0.75, \
                drive_sigma_us=drive_sigma_us,  shots_per_point=1024)
        #Update the Pi Amplitude in CSV file
        rows.append(str(pi_amplitude))
        ###############################################################################################




        ### Q_Scale - Experiemnt Number: 4        ###############################################################################################

        q_s=q_scale(backend, drive_duration_us, drive_sigma_us, precise_q_freq_Hz, amplitude, qubit_n=0, mem_slot=0, num_of_experiments=60, q_s_min=-1.5, q_s_max=+1.5, num_of_shots_per_point=1024)
        #Write q_s value to csv file
        row.append(str(q_s))
        ###############################################################################################




        ### Rabi - Experiment Number: 5
        ###############################################################################################

        pi_amplitude=rabi_experiment(backend=backend, rough_q_freq_Hz=qubit_freq, qubit_n=qubit, \
                mem_slot=0, rabi_points=50, drive_ampl_min=0, drive_ampl_max=0.75, \
                drive_sigma_us=drive_sigma_us,  shots_per_point=1024)
        ###############################################################################################


        ###############################################################################################

        ###############################################################################################

        #Finally writing whole row in the CSV File
        csvwriter.writerow(row)
        row=[]
csv_file.close()


# cross_calib
Implementation of Cross Calibration

After reading this cross_calibration paper -->> https://qudev.phys.ethz.ch/static/content/science/Documents/semester/Andreas_Landig_semesterthesis_131020.pdf

Whatever I understood, the way they make pulses and the sequence of pulses they apply, I have tried to do it with qiskit.pulse

Right now, I have made different python scripts for different experiments like rabi ramsey etc all are within experiments directory and then in a main script cross_calib.py on this directory I will call those pulse functions in the way it has been implemented in the paper.

So, I am just making pulses and sending jobs to ibmq_armonk.

ibmq_armonk overloaded!
actaully, not calibrated for 3 days now!

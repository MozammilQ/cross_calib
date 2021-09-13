# cross_calib
Implementation of Cross Calibration

After reading these paper(s)

-->> https://qudev.phys.ethz.ch/static/content/science/Documents/semester/Andreas_Landig_semesterthesis_131020.pdf

-->> https://qudev.phys.ethz.ch/static/content/science/Documents/semester/Tim_Menke_Semester_Thesis_130829.pdf

-->> https://www.research-collection.ethz.ch/handle/20.500.11850/153681

Whatever I understood, the way they make pulses and the sequence of pulses they apply, I have tried to do it with qiskit.pulse

Right now, I have made different python scripts for different experiments like rabi ramsey etc all are within experiments directory and then in a main script cross_calib.py on this directory I will call those pulse functions in the way it has been implemented in the paper.

So, I am just making pulses and sending jobs to ibmq_armonk.

ibmq_armonk overloaded!
actaully, not calibrated for 3 days now!

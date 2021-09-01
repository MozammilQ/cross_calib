from .common_funx import *

def Pi_Pulse(backend, pi_ampl, qubit_n=0, drive_sigma_us=0.075, pulse_name="pi_pulse"):
    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    with pulse.build(backend) as pi_pulse:
        drive_duration = x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma = pulse.seconds_to_samples(drive_sigma_sec)
        drive_chanl = pulse.drive_channel(qubit_n)
        gussn=pulse.Gaussian(duration=drive_duration, amp=pi_ampl, sigma=drive_sigma_us, name=pulse_name)
        pulse.play(gussn, drive_chanl)

    return pi_pulse


def X90_Pulse(backend, drive_ampl, qubit_n=0, drive_sigma_us=0.075, pulse_name="x90_pulse"):
    drive_sigma_sec=drive_sigma_us*us
    drive_duration_sec=drive_sigma_sec*8

    with pulse.build(backend) as x90_pulse:
        drive_duration=x_16(pulse.seconds_to_samples(drive_duration_sec))
        drive_sigma=pulse.seconds_to_samples(drive_sigma_sec)
        drive_chanl=pulse.drive_channel(qubit_n)
        gauss_pulse=pulse.Gaussian(duration=drive_duration, amp=drive_ampl, sigma=drive_sigma_us, name=pulse_name)
        pulse.play(gauss_pulse, drive_chanl)

    return x90_pulse


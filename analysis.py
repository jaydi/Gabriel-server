import operator
from math import log, floor, sqrt
from cmath import exp, pi 

""" Find a Nearest Power of 2 """
def nearest_power_of_2(n):
    return 2**int(log(n, 2))

""" Fast Fourier Transform (FFT)
    - The Number of Elements in Input List Should be Power of 2 """
def fft(x):
    N = len(x)
    if N <= 1: return x
    even = fft(x[0::2])
    odd  = fft(x[1::2])
    T = [exp(-2j*pi*k/N)*odd[k] for k in range(int(N/2))]
    return [even[k] + T[k] for k in range(int(N/2))] + \
           [even[k] - T[k] for k in range(int(N/2))]

def ifft(x):
    conjugated_x = [each_x.conjugate() for each_x in x]
    conjugated_x = fft(conjugated_x)
    iT = [each_cx.conjugate() for each_cx in conjugated_x]
    return [each_iT / len(iT) for each_iT in iT]

""" One Dimensional(1D) Convolution
    - """
def conv(x, k):
    C = [None]*len(x)
    # Convolution from len(h) to len(x)
    for x_index in range(len(k)-1, len(x)):
        C[x_index] = 0
        j_index = x_index
        for k_index in range(len(k)):
            C[x_index] += x[j_index] * k[k_index]
            j_index -= 1
    # Convolution from 0 to len(h)-1
    for x_index in range(0, len(k)-1):
        C[x_index] = 0
        k_index = 0
        for j_index in range(x_index, -1, -1):
            C[x_index] += x[j_index] * k[k_index]
            k_index += 1
    return C

""" Average """
def average(datas):
    if (len(datas) > 0):
        return sum(datas) / float(len(datas))
    else:
        return 0

""" Standard Deviation """
def std_dev(datas):
    avg = average(datas)
    varis = []
    for data in datas:
        varis.append((data - avg) ** 2)
    return sqrt(sum(varis) / len(varis))

""" Standard Deviation Filter """
def std_dev_filter(datas, size):
    filtered = []
    for i in range(len(datas) - size + 1):
        filtered.append(std_dev(datas[i:i+size]))
    return filtered

""" Step Filter """
def step_filter(datas, threshold):
    filtered = []
    for data in datas:
        if data > threshold:
            filtered.append(1)
        else:
            filtered.append(0)
    return filtered
    
""" Utility Functions """
def normalize(x):
    return [(each_x-min(x))/(max(x)-min(x)) for each_x in x]

def indices(x, func):
    return [index for (index, value) in enumerate(x) if func(value)]

""" Stress Detection """
def stress_detection(hr, eda, acc):
    return (10 / 6 * hr) + eda - (3 * (acc - 1))

class HRDetection(object):

    """ Main Code
         - Processing Input ECG Data in order to Detect Peaks and HR           """
    @classmethod
    def analyzeECG(self, datas):
        # Pre-defined Settings
        SAMPLE_RATE = 100                                           # Sampling Rate (Hz)
        SAMPLE_NUMBER = nearest_power_of_2(len(datas))              # Available Sample Number
        LOW_CUTOFF  = round(SAMPLE_NUMBER*40.00/SAMPLE_RATE)        # Cutoff Frequencies
        HIGH_CUTOFF = 10 #round(SAMPLE_NUMBER*0.067/SAMPLE_RATE)    
        WINDOW_SIZE = floor(SAMPLE_RATE * 571 / 1000)               # Window Size (should be an odd num.)
        if WINDOW_SIZE%2 == 0:
            WINDOW_SIZE += 1

        # Only Can Process the 2^n Inputs
        ecg = datas[0:SAMPLE_NUMBER]

        # Cancellation DC drift
        ecg_mean = sum(ecg)/len(ecg)
        canceled = [(each_item - ecg_mean) for each_item in ecg]

        # Apply Low-Pass and High-Pass Filter
        # - Cutoff Frequency is 0.05Hz(40bpm) for High-Pass Filter
        # - Cutoff Frequency is 4Hz (240bpm) for Low-Pass Filter
        fresult = fft(canceled)
        for index, each_result in enumerate(fresult):
            # High-Pass
            if index <= HIGH_CUTOFF or index >= (SAMPLE_NUMBER - HIGH_CUTOFF):
                fresult[index] = 0
            # Low-Pass
            elif index >= LOW_CUTOFF and index <= (SAMPLE_NUMBER + LOW_CUTOFF):
                fresult[index] = 0
        lh_filtered = [each_ifft.real for each_ifft in ifft(fresult)]

        # Apply Derivative Filter
        deriv_kernel = [(each_item / 8.0) for each_item in [-1, -2, 0, 2, 1]]
        deriv_filtered = conv(lh_filtered, deriv_kernel)
        deriv_filtered = [(each_item / max(deriv_filtered)) for each_item in deriv_filtered]

        # Apply Squarting
        squarted = [(each_item ** 2) for each_item in deriv_filtered]
        squarted = [(each_item / max(squarted)) for each_item in squarted]

        # Apply Moving Window Integration
        mv_kernel = [(each_item / 31) for each_item in range(1, 32)]
        mv_filtered = conv(squarted, mv_kernel)
        mv_filtered = [(each_item / max(mv_filtered)) for each_item in mv_filtered]

        # Apply deviation filter
        window_size = SAMPLE_RATE / 10
        dev_filtered = std_dev_filter(mv_filtered, window_size)

        # Apply step filter
        threshold_value = max(dev_filtered) / 4
        step_filtered = step_filter(dev_filtered, threshold_value)

        # detect peaks
        peak_positions = []
        for i in range(1, len(step_filtered)):
            if step_filtered[i - 1] == 0 and step_filtered[i] == 1:
                peak_positions.append(i)

        # calculate peak intervals
        peak_intervals = []
        for i in range(1, len(peak_positions)):
            peak_intervals.append(peak_positions[i] - peak_positions[i - 1])

        avg_peak_interval = sum(peak_intervals) / float(len(peak_intervals))
        avg_hr_interval = avg_peak_interval / SAMPLE_RATE
        avg_hr = 60 / avg_hr_interval

        # Return Result
        return avg_hr
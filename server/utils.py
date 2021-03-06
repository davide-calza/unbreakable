"""
Copyright (c) 2017 Fondazione Bruno Kessler
Author: Marco Roveri roveri@fbk.eu
See LICENSE.txt for licensing information
See CREDITS.txt for other credits
"""
import numpy as np
from scipy.signal import csd, butter, lfilter, filtfilt, freqz, periodogram, hilbert
from scipy import interpolate

import detect_peaks as dp

import logging

def compute_fft(vibsig, tstep):
    """Computes the FFT of the input signal, and then computes the
    amplitude power spectrum and the frequencies to enable for their
    plot and/or re-use for further computations. It also computes and
    return the fundamental frequency of the input signal.

    vibsig: is the input signal (e.g. a list or a numpy.array)
    tstep: is the timing between two samples in the vibsig

    v_freqs, v_ps, f_freq: the frequencies and the power spectrum for
                   the given signal

    """
    v_sp = np.fft.fft(vibsig)/len(vibsig) # The normalized FFT
    v_ps = np.abs(v_sp)**2 # The power spectrum
    v_freqs = np.fft.fftfreq(len(vibsig), tstep) # The frequency bins
    v_idx = np.argsort(v_freqs)
    fidx = np.argmax(v_ps)
    f_freq = abs(v_freqs[fidx])
    return v_freqs[v_idx], v_ps[v_idx], f_freq

def compute_ifft(vibsig_re, vibsig_im, half=True):
    """Computes the IFFT
    vibsig_re: is the real part of the input signal (e.g. a list
               or a numpy.array)
    vibsig_im: is the immaginary part of the input signal (e.g. a list
               or a numpy.array)
    half: is a boolean that specifies whether the FFT data passed in
          the other two arrays/lists corresponds to a full FFT or to
          an half FFT (the negative frequencies are assumed to be
          symmetric w.r.t. the positive ones).

          If True, the input signal is considered to be constructed as
          follows:

            Let A = vibsig_re + 1j*vibsig_im

            DC = A[0] i.e. the zero frequency term
            A[1:len(A)-1] are the positive frequency terms
            A[-1] is the sum of the values of the positive and
                      negative Nyquist frequencies.

            In this case, the signal can be reconstructed with small
            error. This allows for the use of irfft. An alternative
            to the use of irfft is the use of ifft. In this case the signal
            to pass to the inverse FFT is the following one:
            FFT = [DC ] + A[1:len(A)-1] + [A[-1]] +
                  np.flip(np.conj(A[1:len(A)-1]),0)

    return the ifft of the complex array.

    """

    # check vibsig_re type
    if type(vibsig_re) is np.ndarray:
        v_re = vibsig_re
    elif type(vibsig_re) is list:
        v_re = np.array(vibsig_re)
    else:
        raise TypeError('vibsig_re must be of type list or numpy.ndarray')

    # check vibsig_im type
    if type(vibsig_im) is np.ndarray:
        v_im = vibsig_im
    elif type(vibsig_im) is list:
        v_im = np.array(vibsig_im)
    else:
        raise TypeError('vibsig_im must be of type list or numpy.ndarray')

    v_cplx = v_re + (v_im * 1j)

    if half:
        if False: # Use of the ifft instead of irfft
            P = v_cplx[1:len(v_cplx)-1]
            fft = np.concatenate(([v_cplx[0],], P ))
            fft = np.concatenate((fft, v_cplx[-1]))
            fft = np.concatenate((fft, np.flip(np.conj(P), 0)))
            v_ifft = np.fft.ifft(fft)
            result = v_ifft.real
        else:
            result = np.fft.irfft(v_cplx)
    else:
        v_ifft = np.fft.ifft(v_cplx)
        result = v_ifft.real
    return result


def compute_fundamental_frequency(vibsig, tstep):
    """Computes the fundamental frequency of the given input signal. It
    corresponds to the frequency with maximum amplitude.

    vibsig: is the input signal (e.g. a list or a numpy.array)
    tstep: is the timing between two samples in the vibsig

    freq: the fundamental frequency of the input signal

    """
    _, _, freq = compute_fft(vibsig, tstep)
    return freq

def compute_data_for_spectrum(vibsig, tstep):
    """Computes the proper data to be plot in the web interface, e.g. the
    spectrum, and the peaks.  Returns four arrays (f, a) for the power
    spectrum (first and second return elements), and (f, v)
    corresponding to the peaks (thrid and fourth return elements).
    The last argument is the fundamental frequency of the input signal.
    """
    f_freqs, v_ps, f_freq = compute_fft(vibsig, tstep)
    mph = max(v_ps)/4.0
    pidx = dp.detect_peaks(v_ps, mph=mph)
    f_p_v = v_ps[pidx]
    f_p_f = f_freqs[pidx]
    return f_freqs, v_ps, f_p_f, f_p_v, f_freq

def interp(x, y, oob_extrapolate=False):
    """ Leverages on scypi to create an interpolator to
        evaluate the function (x,y) in any point also not
        specified in x,y.

        This allows to write f(h) for any h

        This function for values outside the given bands for x
        and y will return 0.0. if oob_extrapolate is False, otherwise
        it leverages on the extrapolation methods to compute the value.

        """
    kind = 'linear' # or a number to specify order of spline
    if oob_extrapolate:
        f = interpolate.interp1d(x, y, fill_value='extrapolate', kind=kind)
    else:
        f = interpolate.interp1d(x, y, fill_value=(0.0, 0.0), bounds_error=False, kind=kind)
    return f

def mhs(amplitude, freq, phase=None, plot=False):
    """
    amplitude: is the hilbert spectrum amplitude signal
               resulting from hilbert transformation
    freq: is the instantaneous frequency resulting
               from hilbert transformation

    returns A, F where A is the sum of the contribution
                 of each frequency component in the freq
                 vector for all time points, and F is the
                 frequency axis where to interpret A.
    """
    f = np.array(freq)
    HS = np.array(amplitude)
    Atemp = []
    F = []
    i = 1
    while f.size != 0:
        # indx = [i for i,v in enumerate(f) if v = f[0]]
        indx = np.argwhere(f == f[0]).flatten()
        F += [f[0]]
        Atemp += [np.sum(HS[indx])]
        HS[indx] = 0
        f[indx] = 0;
        HS = HS[HS != 0]
        f = f[f != 0]
        i = i + 1

    F = np.array(F)
    indx = np.argsort(F)
    F = F[indx]
    A = np.array(Atemp)[indx]
    if plot:
        import matplotlib.pyplot as plt
        plt.subplot(4, 1, 1)
        plt.plot(amplitude, 'b')
        plt.subplot(4, 1, 2)
        plt.plot(F, A, 'r')
        plt.subplot(4, 1, 3)
        if phase is not None:
            plt.plot(phase, 'r')
        plt.subplot(4, 1, 4)
        plt.plot(freq, 'r')
        plt.show()

    return A, F

def LP_filter(cutoff, fs, data, order=6, plot=False):
    l = logging.getLogger('UTILS')
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    if (normal_cutoff >= 0) and (normal_cutoff <= 1):
        b, a = butter(order, normal_cutoff, btype='low')
        y = lfilter(b, a, data)
        l.debug("LP_filter: normalized cutoff %s is in [0,1]!" % normal_cutoff)
    else:
        y = data
        l.debug("LP_filter: normalized cutoff %s is not in [0,1]!" % normal_cutoff)
        l.debug("LP_filter: cutoff: %s, fs: %s" % (cutoff, fs))
        l.debug("LP_filter: no LP filter applied")

    if plot:
        import matplotlib.pyplot as plt
        w, h = freqz(b, a, worN=8000)
        plt.subplot(2, 1, 1)
        plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
        plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
        plt.axvline(cutoff, color='k')
        plt.xlim(0, 0.5*fs)
        plt.title("Lowpass Filter Frequency Response (AA)")
        plt.xlabel('Frequency [Hz]')
        plt.grid()
        plt.show()

    return y

def HP_filter(cutoff, fs, data, order=6, plot=False):
    l = logging.getLogger('UTILS')
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    if (normal_cutoff >= 0) and (normal_cutoff <= 1):
        b, a = butter(order, normal_cutoff, btype='high')
        y = filtfilt(b, a, data)
        l.debug("HP_filter: normalized cutoff %s is in [0,1]!" % normal_cutoff)
    else:
        l.debug("HP_filter: normalized cutoff %s is not in [0,1]!" % normal_cutoff)
        l.debug("HP_filter: cutoff: %s, fs: %s" % (cutoff, fs))
        l.debug("LP_filter: no HP filter applied")
        y = data

    if plot:
        import matplotlib.pyplot as plt
        w, h = freqz(b, a, worN=8000)
        plt.subplot(2, 1, 1)
        plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
        plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
        plt.axvline(cutoff, color='k')
        plt.xlim(0, 0.5*fs)
        plt.title("Highpass Filter Frequency Response")
        plt.xlabel('Frequency [Hz]')
        plt.grid()
        plt.show()

    return y

def hilb(s, unwrap=True):
    """
    Performs Hilbert transformation on signal s.
    Returns amplitude and phase of signal.
    Depending on unwrap value phase can be either
    in range [-pi, pi) (unwrap=False) or
    continuous (unwrap=True).
    """
    H = hilbert(s)

    amp = np.abs(H)
    phase = np.arctan2(H.imag, H.real)

    if unwrap: phase = np.unwrap(phase)

    return H, amp, phase

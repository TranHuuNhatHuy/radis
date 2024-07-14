# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 17:48:14 2024

@author: Nicolas Minesi

"""
from radis import SpectrumFactory, plot_diff
from radis.test.utils import getValidationCase
import pytest

@pytest.mark.needs_connection
def test_Kurucz_vs_NISTandSpectraplot(plot=True, verbose=True):
    def broad_arbitrary(**kwargs):
        """An arbitrary broadening formula in SpectraPlot (https://spectraplot.com/)"""
        return 1 * (296 / kwargs["Tgas"]) ** 0.8, None

    #%% Employ the same inputs than in example file 'spectraplot_O_10000K.txt'
    sf = SpectrumFactory(
        wavelength_min=777,
        wavelength_max=778,
        wstep=0.001,
        species="O_I",
        optimization="simple",
        path_length=1,  # cm
        pressure=1,  # atm
        verbose=0,
        lbfunc=broad_arbitrary,
    )
    sf.fetch_databank("kurucz", parfuncfmt="kurucz")
    # sf.load_databank('Kurucz-O_I', drop_columns=[], load_columns='all')
    s_RADIS = sf.eq_spectrum(Tgas=10000, name="Kurucz by RADIS")
    # s_RADIS.plot("radiance_noslit", wunit="cm-1")

    #%% Experimental spectrum
    import numpy as np

    from radis import Spectrum

    L = 1  # cm - Input in SpectraPlot software
    raw_data = np.loadtxt(getValidationCase("spectraplot_O_10000K.txt"), delimiter=",", skiprows=1)
    s_SpectraPlot = Spectrum(
        {
            "wavenumber": raw_data[:, 0],
            "abscoeff": raw_data[:, 1]
            / L,  # spectraplot outputs absorbance; abscoef = absorbance / L
        },
        units={"abscoeff": "cm-1"},
        wunit="cm-1",
        name="NIST by SpectraPlot",
    )
    # s_SpectraPlot.plot('abscoeff', wunit='cm-1')

    if plot:
        plot_diff(s_RADIS, s_SpectraPlot, "abscoeff", wunit="nm")
    A_RADIS = s_RADIS.get_integral("abscoeff", wunit="nm")
    A_SpectraPlot = s_SpectraPlot.get_integral("abscoeff", wunit="nm")

    if verbose:
        print(
            f"Ratio of area under abscoef ('k') is A_RADIS/A_SpectraPlot = {A_RADIS/A_SpectraPlot:.3f}"
        )

    assert np.isclose(A_RADIS, A_SpectraPlot, rtol=1e-2)


if __name__ == "__main__":
    test_Kurucz_vs_NISTandSpectraplot()

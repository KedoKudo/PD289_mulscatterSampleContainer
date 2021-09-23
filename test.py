#!/usr/bin/env python
"""
Prototype of unit test for multiple scattering data
"""

from mantid.simpleapi import (
    ConvertUnits,
    CreateSampleWorkspace,
    EditInstrumentGeometry,
    SetSample,
    MayersSampleCorrection,
    CalculateCarpenterSampleCorrection,
    MultipleScatteringCorrection,
    CompareWorkspaces,
)

import numpy as np


# prep example data
def make_sample_workspace():
    # Create a fake workspace with TOF data
    sample_ws = CreateSampleWorkspace(Function='Powder Diffraction',
                                      NumBanks=2,
                                      BankPixelWidth=1,
                                      XUnit='TOF',
                                      XMin=1000,
                                      XMax=1500,)
    # fake instrument
    EditInstrumentGeometry(sample_ws,
                           PrimaryFlightPath=5.0,
                           SpectrumIDs=[1, 2],
                           L2=[2.0, 2.0],
                           Polar=[10.0, 90.0],
                           Azimuthal=[0.0, 45.0],
                           DetectorIDs=[1, 2],
                           InstrumentName="Instrument")
    return sample_ws


def add_cylinder_sample_to_workspace(
        ws,
        material,
        number_density,
        mass_density,
        center_bottom_base=[0.0, 0.0, 0.0],  # x,y,z of bottom base of cylinder
        height=0.1,  # in meter
        radius=0.1,  # in meter
):
    SetSample(
        ws,
        Geometry={
            "Shape": "Cylinder",
            "centre-of-bottom-base": {
                "x": center_bottom_base[0],
                "y": center_bottom_base[1],
                "z": center_bottom_base[2],
            },
            "Height": height,
            "Radius": radius,
            "Axis": 1,
        },
        Material = {
            "ChemicalFormula": material,
            "SampleNumberDensity": number_density,
            "SampleMassDensity": mass_density,
        }
    )
    return ws


# use Mayers correction
def correction_Mayers(sample_ws):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target="TOF",
                 EMode="Elastic")
    rst = MayersSampleCorrection(sample_ws, MultipleScattering=True)
    return rst


# use Carpenter correction
def correction_carpenter(sample_ws):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target="Wavelength",
                 EMode="Elastic")
    rst = CalculateCarpenterSampleCorrection(sample_ws)
    return rst


# use Mutliple scattering correction
def correction_multiple_scattering(sample_ws, unit="Wavelength"):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target=unit,
                 EMode="Elastic")
    rst = MultipleScatteringCorrection(sample_ws)
    return rst


if __name__ == "__main__":
    print("running exmaple test")
    # ---
    # TEST_1: Vanadium In-plane only
    # ---
    ws = make_sample_workspace()
    # add cylinder sample
    # standard sample container on POWGEN
    ws = add_cylinder_sample_to_workspace(
        ws,
        "V",
        0.07261,
        6.11,
        [0.0, -0.0284, 0.0],
        0.00295,
        0.0568,
    )

    # use Mayers correction
    mayers_multi = correction_Mayers(ws)

    # use Carpenter correction
    carpenter_multi = correction_carpenter(ws)

    # use Multiple scattering correction
    ms_multi = correction_multiple_scattering(ws)

    # validation
    # -- cast to wavelength
    ws = ConvertUnits(ws, "Wavelength")
    mayers_multi = ConvertUnits(mayers_multi, "Wavelength")
    carpenter_multi = ConvertUnits(carpenter_multi, "Wavelength")
    ms_multi = ConvertUnits(ms_multi, "Wavelength")
    # -- compute difference
    CompareWorkspaces(Workspace1='carpenter_multi',
                      Workspace2='ms_multi',
                      CheckInstrument=False,
                      CheckMasking=False)

    """
    # ---
    # TEST_2: Diamond
    ws = make_sample_workspace()
    # standard sample container on POWGEN
    ws = add_cylinder_sample_to_workspace(
        ws,
        "C",
        176.2,  # 10^27/m^3 (https://en.wikipedia.org/wiki/Number_density)
        3.515,  # g/cm^3 (https://en.wikipedia.org/wiki/Carbon)
        [0.0, -0.0284, 0.0],
        0.00295,
        0.0568,
    )
    # use Mayers correction
    mayers_multi = correction_Mayers(ws)
    # use Multiple scattering correction
    ms_multi = correction_multiple_scattering(ws)
    # validation
    # -- cast to wavelength
    mayers_multi = ConvertUnits(mayers_multi, "Wavelength")
    ms_multi = ConvertUnits(ms_multi, "Wavelength")
    # -- compute difference
    """
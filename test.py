#!/usr/bin/env python
"""
Prototype of unit test for multiple scattering data
"""

from mantid.simpleapi import (
    ConvertUnits,
    CreateSampleWorkspace,
    EditInstrumentGeometry,
    SetSample,
    MultipleScatteringCorrection,
)

# ----------------------- #
# make an empty workspace #
# ----------------------- #
# Create a fake workspace with TOF data
ws = CreateSampleWorkspace(Function='Powder Diffraction',
                            NumBanks=2,
                            BankPixelWidth=1,
                            XUnit='TOF',
                            XMin=1000,
                            XMax=1500,)
# Fake instrument
EditInstrumentGeometry(ws,
                        PrimaryFlightPath=5.0,
                        SpectrumIDs=[1, 2],
                        L2=[2.0, 2.0],
                        Polar=[10.0, 90.0],
                        Azimuthal=[0.0, 45.0],
                        DetectorIDs=[1, 2],
                        InstrumentName="Instrument")
# set sample and container
SetSample(
        ws,
        Geometry={
            "Shape": "Cylinder",
            "Center": [0., 0., 0.],
            "Height": 1.0,
            "Radius": 0.2,
        },
        Material = {
            "ChemicalFormula": "La-(B11)5.94-(B10)0.06",
            "SampleNumberDensity": 0.1,
        },
        ContainerMaterial = {
            "ChemicalFormula": "V",
            "SampleNumberDensity": 0.0721,
        },
        ContainerGeometry = {
            "Shape": "HollowCylinder",
            "Height": 1.0,
            "InnerRadius": 0.2,
            "OuterRadius": 0.3,
            "Center": [0., 0., 0.],
        }
    )

# to wavelength
ConvertUnits(InputWorkspace=ws,
                OutputWorkspace=ws,
                Target="Wavelength",
                EMode="Elastic")

# Run the multiple scattering correction
rst = MultipleScatteringCorrection(
    InputWorkspace = ws,
    Method="SampleAndContainer",
    ElementSize=0.1,  # mm
)

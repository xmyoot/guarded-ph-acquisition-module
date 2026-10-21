"""Architecture arithmetic only; no CAD, simulation, firmware or hardware tests."""
import json
import math
from pathlib import Path

vref = 2.048
gain = 2
vcm = vref / 2
signal_max = 0.600
slope_25 = 0.05916
rail_min = 3.3 * (1 - 0.015)
uncertainty = 0.010
ain_min = vcm - signal_max - uncertainty
ain_max = vcm + signal_max + uncertainty
lsb = vref / (gain * 32768)
result = {
    "status": "calculated proposal; not measured or simulated",
    "input_assumptions": {
        "reference_V": vref,
        "adc_total_gain": gain,
        "signal_envelope_V": [-signal_max, signal_max],
        "common_mode_uncertainty_allocation_V": uncertainty,
        "analog_rail_tolerance_fraction": 0.015,
        "probe_resistance_ohm": 1e9,
    },
    "reference_VCM_V": vcm,
    "rail_min_V": rail_min,
    "ain_range_including_allocation_V": [ain_min, ain_max],
    "adc_equation_6_limits_V": [0.2, rail_min - 0.2],
    "adc_lower_margin_V": ain_min - 0.2,
    "adc_upper_margin_V": rail_min - 0.2 - ain_max,
    "lmp_300mV_characterization_lower_margin_V": ain_min - 0.3,
    "differential_full_scale_V": vref / gain,
    "differential_range_margin_V": vref / gain - signal_max,
    "adc_LSB_V": lsb,
    "adc_LSB_pH_equivalent_25C": lsb / slope_25,
    "nominal_code_at_600mV": signal_max / lsb,
    "filter_pole_Hz": 1 / (2 * math.pi * (1000 + 1000) * 10e-9),
    "I2C_rise_time_100pF_ns": 0.8473 * 4700 * 100e-12 * 1e9,
    "I2C_rise_time_200pF_ns": 0.8473 * 4700 * 200e-12 * 1e9,
    "bias_error_at_125fA_1Gohm_V": 125e-15 * 1e9,
    "bias_error_pH_equivalent_25C": 125e-15 * 1e9 / slope_25,
    "board_leakage_allocation_error_V": 100e-15 * 1e9,
    "reference_initial_error_at_600mV_V": 0.002 * signal_max,
    "reference_initial_error_pH_equivalent_25C": 0.002 * signal_max / slope_25,
    "insulation_for_1V_100fA_ohm": 1 / 100e-15,
    "LDO_power_at_allocated_10mA_W": (5 - 3.3) * 0.010,
    "electronics_0p01pH_objective_V": slope_25 * 0.01,
}
assert ain_min > 0.2
assert ain_max < rail_min - 0.2
assert signal_max < vref / gain
Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

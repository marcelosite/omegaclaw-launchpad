; Illustrative MeTTa lesson scaffold for the synthetic factory-fault fixture.
; Studio P0 does not execute this file in the real OmegaClaw runtime.
; It represents only a recommendation for manual inspection.

(= (manual_inspection_recommended)
   (and (temperature_above_demo_threshold)
        (vibration_above_demo_threshold)))

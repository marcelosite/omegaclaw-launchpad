; Exact NAL teaching expressions for The Lighthouse in the Fog.
; The proof runner hashes this file before invoking the pinned runtime.

; Initial conflicting reports: revision should expose disagreement.
(|- ((--> north_route clear) (stv 0.95 0.75))
    ((--> north_route clear) (stv 0.15 0.75)))

; Current independent confirmations: revision should strengthen support.
(|- ((--> north_route clear) (stv 1.0 0.95))
    ((--> north_route clear) (stv 1.0 0.90)))

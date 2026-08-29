# Example receipt — fixture only

**Status:** lesson fixture, not a real patient-care decision

## Recorded input

The fictional case contains an observed triage-capacity note, a missing
consent record, and two agent positions: `route_to_clinic` and
`request_more_information`.

## Human rule

When the agents disagree or a required consent fact is missing, recommend
`human_review_required`.

## Result

`human_review_required`

No message was sent, no record was changed, and no care was denied. This
fixture does not provide medical advice, a diagnosis, causal finding, or
validation of external data. A human must review any real case.

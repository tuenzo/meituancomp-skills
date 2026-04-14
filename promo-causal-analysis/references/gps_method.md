# GPS Method

## Role

Use GPS to estimate how the outcome changes with continuous treatment intensity. This layer refines scaling logic after the main increment has been established by LocalGap.

## Questions It Answers

- does response increase smoothly with more intensity
- where do diminishing returns begin
- is there evidence of saturation or unstable tails

## Typical Treatment Variables

- `discount_rate`
- `view_uv`
- combined intensity score when exposure and discount are both present

## Recommended Outcome Variables

- `local_gap` when available
- `gmv` only when LocalGap is unavailable and the downgrade is disclosed

## Estimation Sequence

1. define the continuous treatment variable
2. estimate the generalized propensity score
3. fit a response surface using treatment and GPS terms
4. derive the dose-response curve over the supported region

## Diagnostics

Always report:

- treatment support range
- overlap quality
- whether the curve is monotonic, flattening, or unstable

## Interpretation

Use GPS to interpret marginal scaling logic, not to overwrite LocalGap.

If the curve is flat or unstable at higher doses, conclude that more intensity may not yield proportional gain even when current increment is positive.

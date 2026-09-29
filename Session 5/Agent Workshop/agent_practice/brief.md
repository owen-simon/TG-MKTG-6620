# Northline Outfitters: next week's campaign decision

Original fictional classroom data, authored September 28, 2026. These are
daily campaign-by-segment aggregates, not people, orders, or a randomized trial.
The decision is whether the marketing manager has enough evidence to move
next week's budget from campaign A to campaign B.

One row should represent one record_id. The export accidentally repeated
C008 with exactly the same values. Retain one copy of an exact duplicate;
stop for review if the same ID has conflicting values. Preserve the input.
Zeros are observed zeros; missing values must not silently become zeros.

Visits are site visits, not unique customers. Orders are orders attributed to
those visits under the same fictional reporting rule for both campaigns.
For this exercise conversion means total orders divided by total visits.
Revenue and advertising spend are US dollars, not cents. Refunds are linked
back to the attributed orders and include all known refunds for this frozen
extract. Net revenue means gross revenue minus refunds. Costs of goods,
fulfillment, and other operating costs are unavailable, so profit is unknown.
Net revenue divided by advertising spend is a revenue-to-spend ratio, not ROI.

The file covers September 14–15 only. Campaigns reached different mixes of
new and returning visitors. Assignment was not randomized. No customer-level
outcomes or later outcomes are supplied. A pooled difference does not identify
what would happen if the same audience were switched from one campaign to the
other. A 50/50 new/returning audience is an optional hypothetical scenario,
not a claim about next week's traffic.

Required evidence for a recommendation: row audit; campaign totals and
orders/visits; campaign-by-segment orders/visits; net revenue and spend; the
limits on causal and profit claims; one useful next measurement. A decision
to hold, test, or reallocate a bounded amount is acceptable if its reasoning
matches the evidence and explicitly states its assumptions.

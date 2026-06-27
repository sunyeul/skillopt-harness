# SkillOpt Gate Decision

- Decision: `accept_new_best`
- Leakage status: `clean`
- Parent selection score: `0.800`
- Candidate selection score: `1.000`
- Best selection score: `0.800`
- Reporting-only parent/current-best test score: `0.600`
- Reporting-only accepted candidate test score: `0.600`
- Reporting-only test delta: `0.000`
- Rollout isolation: `independent`

Strict improvement is required over the parent/current skill. `accept_new_best` additionally requires improvement over the recorded best.
Test scores were measured only after selection adoption for reporting and did
not influence the gate decision.

# Test Reporting Notes

Test split repair and grading happened only after the clean selection gate and
`accept_new_best` adoption. These scores are reporting-only and did not affect
candidate acceptance, rejection, or skill text.

- Parent/baseline reporting repairer: subagent
  `019f0a09-51dc-7ed1-9c58-00f9c4a18595` (`Heisenberg`), assigned
  `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`.
- Candidate/current-best reporting repairer: subagent
  `019f0a09-77ef-7a80-a4ab-2991bfa605f8` (`Linnaeus`), assigned
  `runs/data-normalization-skillopt-20260627/loop-01/candidate-skill.md`.
- Parent/baseline test score: `3/5 = 0.6`.
- Candidate/current-best test score: `3/5 = 0.6`.
- Test delta: `0.0`.
- Same ordered task ids were present in both test JSONL files.

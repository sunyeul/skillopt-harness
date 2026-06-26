# Evidence Timeline

1. Read loop discipline, AGENTS.md, `skillopt.yaml`, target parent skill, and auditor prompt.
2. Created experiment lineage and loop parent snapshot before reading task evidence.
3. Listed and prepared only `code_repair` train tasks through explicit train-split harness commands.
4. Inspected prepared train workspaces only: `task.json`, source files, and `tests_visible`.
5. Repaired train workspaces using the parent skill, ran visible tests, and graded train workspaces with redacted output.
6. Wrote reflect protocol, rejected-edit memory, train trajectories, edit proposals, candidate skill, and update report using train evidence only.
7. Candidate skill was frozen before any selection or test evidence was observed.
8. Selection rollout delegated to isolated repairers:
   - parent repairer: Curie (`019f04e1-7d09-7320-9792-a887f84b1bae`)
   - candidate repairer: James (`019f04e1-7e15-7c73-9187-79a818f6ab55`)
9. Parent selection repairer reported `0/5`; candidate selection repairer was
   independent and had no access to parent output.
10. Candidate selection repairer reported `3/5`.
11. Selection records covered the same five tasks in the same order.
12. `loop-run` recorded `accept_new_best`, `clean` leakage, parent score `0.0`,
    candidate score `0.6`, and rollout isolation `independent`.
13. Independent auditor reported `accept_new_best`, `clean`, no blocking
    condition, no cleanup, and high confidence.
14. After adoption, accepted current-best was measured on test for reporting:
    `5/5`, score `1.0`.
15. After adoption, immutable initial baseline was measured on test by an
    isolated repairer for post-hoc reporting only: `2/5`, score `0.4`.

Test evidence was observed only after adoption and was not used for candidate
generation, selection, or later skill edits.

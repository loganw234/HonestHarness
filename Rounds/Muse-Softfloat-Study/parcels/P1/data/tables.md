## T1 Tokens by model (figures.json `tokens_by_model`)

| model | usage rows | input | output | input+output | cached |
|---|---|---|---|---|---|
| muse-spark-1.3 | 59 | 677,616,961 | 3,289,230 | 680,906,191 | 664,524,584 |
| muse-wonder-full-1.0 | 69 | 733,186,697 | 3,972,310 | 737,159,007 | 714,631,920 |

## T2 Tokens by role (role from the agent's passes row; `tokens_by_role`)

| role | usage rows | input | output | input+output |
|---|---|---|---|---|
| author | 28 | 485,845,099 | 2,244,302 | 488,089,401 |
| author+fixer | 1 | 7,101,595 | 47,604 | 7,149,199 |
| fixer | 3 | 14,778,009 | 71,247 | 14,849,256 |
| surveyor | 50 | 276,331,105 | 1,976,661 | 278,307,766 |
| verifier | 46 | 626,747,850 | 2,921,726 | 629,669,576 |

## T3 Passes by wave and role (`passes_by_wave_role`)

| wave | author | fixer | surveyor | verifier |
|---|---|---|---|---|
| polish | 0 | 0 | 10 | 1 |
| wave0 | 1 | 0 | 16 | 10 |
| wave1 | 2 | 2 | 1 | 5 |
| wave2 | 2 | 0 | 2 | 2 |
| wave3 | 2 | 0 | 3 | 1 |
| wave4 | 4 | 0 | 6 | 6 |
| wave5 | 11 | 1 | 8 | 14 |
| wave6 | 9 | 1 | 4 | 7 |

## T4 Verifier passes by wave: count, a, b (`verifier_passes_by_wave`, `verifier_ab_by_wave`)

| wave | verifier passes | a | b |
|---|---|---|---|
| polish | 1 | 4 | 0 |
| wave0 | 10 | 0 | 14 |
| wave1 | 5 | 4 | 7 |
| wave2 | 2 | 4 | 7 |
| wave3 | 1 | 1 | 4 |
| wave4 | 6 | 12 | 14 |
| wave5 | 14 | 55 | 24 |
| wave6 | 7 | 29 | 8 |

## T5 Plants by wave (`plants_by_wave`)

| wave | plants | caught | missed |
|---|---|---|---|
| polish | 5 | 4 | 1 |
| postseal | 25 | 25 | 0 |
| readme | 10 | 9 | 1 |
| site | 10 | 10 | 0 |
| wave1 | 10 | 9 | 1 |
| wave2 | 10 | 10 | 0 |
| wave3 | 5 | 5 | 0 |
| wave4 | 25 | 25 | 0 |
| wave5 | 50 | 46 | 4 |
| wave6 | 45 | 44 | 1 |

## T6 Recall by class (recall_by_class.csv)

| class | n | caught | missed | recall | wilson95_lo | wilson95_hi | note |
|---|---|---|---|---|---|---|---|
| code | 87 | 87 | 0 | 1.000 | 0.958 | 1.0 |  |
| claim in docs | 60 | 56 | 4 | 0.933 | 0.841 | 0.974 |  |
| test data | 34 | 32 | 2 | 0.941 | 0.809 | 0.984 |  |
| metadata or provenance | 8 | 6 | 2 | 0.750 | 0.409 | 0.929 | n < 10: too small to rank |
| other | 3 | 3 | 0 | 1.000 | 0.438 | 1.0 | n < 10: too small to rank |
| record arithmetic | 3 | 3 | 0 | 1.000 | 0.438 | 1.0 | n < 10: too small to rank |

## T7 Recall by verifier model (recall_by_model.csv)

| model | n | caught | missed | recall | wilson95_lo | wilson95_hi | note |
|---|---|---|---|---|---|---|---|
| muse-spark-1.3 | 185 | 178 | 7 | 0.962 | 0.924 | 0.982 |  |
| not recorded | 10 | 9 | 1 | 0.900 | 0.596 | 0.982 |  |

## T8 Recall by project (recall_by_project.csv)

| project | n | caught | missed | recall | wilson95_lo | wilson95_hi | note |
|---|---|---|---|---|---|---|---|
| library | 195 | 187 | 8 | 0.959 | 0.921 | 0.979 |  |
| toy (plants inside verdict rows) | 220 | 220 | 0 | 1.000 | 0.983 | 1.0 |  |

## T9 Recall by wave (recall_by_wave.csv)

| wave | n | caught | missed | recall | wilson95_lo | wilson95_hi | note |
|---|---|---|---|---|---|---|---|
| wave5 | 50 | 46 | 4 | 0.920 | 0.812 | 0.968 |  |
| wave6 | 45 | 44 | 1 | 0.978 | 0.884 | 0.996 |  |
| postseal | 25 | 25 | 0 | 1.000 | 0.867 | 1.0 |  |
| wave4 | 25 | 25 | 0 | 1.000 | 0.867 | 1.0 |  |
| readme | 10 | 9 | 1 | 0.900 | 0.596 | 0.982 |  |
| site | 10 | 10 | 0 | 1.000 | 0.722 | 1.0 |  |
| wave1 | 10 | 9 | 1 | 0.900 | 0.596 | 0.982 |  |
| wave2 | 10 | 10 | 0 | 1.000 | 0.722 | 1.0 |  |
| polish | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| wave3 | 5 | 5 | 0 | 1.000 | 0.566 | 1.0 | n < 10: too small to rank |

## T10 Verifiers below 5 of 5 (from recall_by_verifier.csv; the other verifiers are 5 of 5)

| verifier | n | caught | missed | recall | wilson95_lo | wilson95_hi | note |
|---|---|---|---|---|---|---|---|
| verifier-polish1 | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| verifier-readme | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| verifier-sf2 | 5 | 3 | 2 | 0.600 | 0.231 | 0.882 | n < 10: too small to rank |
| verifier-w1f32 | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| verifier-w5alg1 | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| verifier-w5metrics | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |
| verifier-w6metrics | 5 | 4 | 1 | 0.800 | 0.376 | 0.964 | n < 10: too small to rank |

## T11 Escalations (`escalations`)

| kind | n | answered | unanswered | min s | median s | max s |
|---|---|---|---|---|---|---|
| test | 11 | 6 | 5 | 19.0 | 179.0 | 438.0 |
| real | 12 | 12 | 0 | 38.0 | 141.5 | 3864.0 |

## T12 Agents with no usage and no passes row (agents_without_rows.csv)

| agent | plant rows |
|---|---|
| auditor-adherence-seal | 0 |
| lead-polish1 | 0 |
| lead-seam | 0 |
| parcel-psbench | 0 |
| parcel-psbench2 | 0 |
| parcel-psciwindows | 0 |
| parcel-psedge | 0 |
| parcel-psreadme | 0 |
| parcel-w6captions | 0 |
| parcel-w6metrics | 0 |
| verifier-psbench | 5 |
| verifier-psbench2 | 5 |
| verifier-psciwindows | 5 |
| verifier-psedge | 5 |
| verifier-psreadme | 5 |
| verifier-w6captions | 5 |
| verifier-w6metrics | 5 |

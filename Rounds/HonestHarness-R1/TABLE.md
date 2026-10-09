# HonestHarness round 1: the table

Drawn by `python tools/table.py` from `records/`, with the batches named in
`table-batches.json`; nothing here is typed by hand. Each suite pools its own
records with its own function. The score of record for QS4 and QS4h is the
lead's judgement, checked by a verifier (`qs/suites/qs4_judgements.json`,
`qs4h_judgements.json`); "screen" is the script's marker screen.

## QS1

| thinking | suite version | runs | statuses | trigger F1 (tp/fp/fn/tn) | agreement | schema valid | reasoning emitted |
|---|---|---|---|---|---|---|---|
| off | 1.3765303639a2.2ff54c82d6f4 | 105 | pass 105 | 1.000 (87/0/0/42) | 129/129 (1.000) | 118/118 (1.000) | n/a |
| on | 1.3765303639a2.2ff54c82d6f4 | 105 | pass 90, refused 15 | 1.000 (87/0/0/39) | 126/126 (1.000) | 102/102 (1.000) | 80/132 (0.606) |

## QS6

| cut | set | thinking | exact | overclaimed | not scored | median prompt tokens |
|---|---|---|---|---|---|---|
| c016k | length | off | 36/36 (1.000) | n/a | none | 17610 |
| c016k | length | on | 36/36 (1.000) | n/a | none | 17635 |
| c016k | reach | off | 6/6 (1.000) | 0/24 (0.000) | none | 17608.5 |
| c016k | reach | on | 6/6 (1.000) | 0/24 (0.000) | none | 17633.5 |
| c032k | length | off | 36/36 (1.000) | n/a | none | 32910 |
| c032k | length | on | 36/36 (1.000) | n/a | none | 32935 |
| c032k | reach | off | 9/9 (1.000) | 0/21 (0.000) | none | 32908.5 |
| c032k | reach | on | 9/9 (1.000) | 0/21 (0.000) | none | 32933.5 |
| c064k | length | off | 36/36 (1.000) | n/a | none | 64572 |
| c064k | length | on | 36/36 (1.000) | n/a | none | 64597 |
| c064k | reach | off | 12/12 (1.000) | 0/18 (0.000) | none | 64570.5 |
| c064k | reach | on | 12/12 (1.000) | 0/18 (0.000) | none | 64595.5 |
| c128k | length | off | 36/36 (1.000) | n/a | none | 139232 |
| c128k | length | on | 36/36 (1.000) | n/a | none | 139257 |
| c128k | reach | off | 24/24 (1.000) | 0/6 (0.000) | none | 139230.5 |
| c128k | reach | on | 24/24 (1.000) | 0/6 (0.000) | none | 139255.5 |
| whole | length | off | 35/36 (0.972) | n/a | none | 154183 |
| whole | length | on | 36/36 (1.000) | n/a | none | 154208 |
| whole | reach | off | 30/30 (1.000) | n/a | none | 154181.5 |
| whole | reach | on | 30/30 (1.000) | n/a | none | 154206.5 |

## QS4

| run | item | status | plants caught, screen | plants caught, judged | findings | round 6's in-view findings located | read | output | cost |
|---|---|---|---|---|---|---|---|---|---|
| qs4-p2-planted-20261007T103409Z.p2-planted.r0 | p2-planted | fail | 1 | 1 | 3 | 1/3 | 4201807 | 67573 | 0.069662466 |
| qs4-p2-real-20261007T110448Z.p2-real.r0 | p2-real | pass | 0 | None | 2 | 0/2 | 9184171 | 184155 | 0.155230842 |
| qs4-p1-planted-20261007T112510Z.p1-planted.r0 | p1-planted | pass | 2 | 2 | 3 | 1/6 | 5599463 | 67862 | 0.073787754 |
| qs4-p1-real-20261007T113404Z.p1-real.r0 | p1-real | pass | 0 | None | 2 | 1/6 | 27285952 | 215133 | 0.240356472 |
| qs4-p3-planted-20261007T120601Z.p3-planted.r0 | p3-planted | pass | 2 | 2 | 2 | 0/2 | 6437129 | 62724 | 0.074859942 |
| qs4-p3-real-20261007T121519Z.p3-real.r0 | p3-real | pass | 0 | None | 1 | 0/2 | 18486697 | 217297 | 0.208141278 |
| qs4-p4-planted-20261007T125519Z.p4-planted.r0 | p4-planted | pass | 2 | 1 | 2 | 0/0 | 5856813 | 70361 | 0.076991478 |
| qs4-p4-real-20261007T130515Z.p4-real.r0 | p4-real | pass | 0 | None | 1 | 0/0 | 13049750 | 215322 | 0.189193812 |
| qs4-p5-planted-20261007T132806Z.p5-planted.r0 | p5-planted | pass | 2 | 2 | 4 | 1/5 | 12773531 | 100537 | 0.124725738 |
| qs4-p5-real-20261007T134511Z.p5-real.r0 | p5-real | stopped | None | None | None | None/None | 40176389 | 269875 | 0.316530678 |
| qs4-p3-planted-20261007T142258Z.p3-planted.r0 | p3-planted | pass | 2 | 2 | 2 | 0/2 | 5865558 | 99527 | 0.092265420 |
| qs4-p4-planted-20261007T143555Z.p4-planted.r0 | p4-planted | fail | 1 | 1 | 1 | 0/0 | 7280457 | 98425 | 0.100231134 |
| qs4-p5-real-20261007T151656Z.p5-real.r0 | p5-real | pass | 0 | None | 6 | 3/5 | 26564802 | 249560 | 0.261690732 |
| qs4-p1-planted-20261007T155708Z.p1-planted.r0 | p1-planted | pass | 2 | 2 | 2 | 0/6 | 4878404 | 52508 | 0.060487800 |
| qs4-p5-planted-20261007T160649Z.p5-planted.r0 | p5-planted | fail | 1 | 1 | 2 | 0/5 | 10676085 | 84890 | 0.104862462 |
| qs4-p2-planted-20261007T161904Z.p2-planted.r0 | p2-planted | pass | 2 | 2 | 3 | 1/3 | 5564499 | 60956 | 0.069178818 |
| qs4-p4-real-20261007T163001Z.p4-real.r0 | p4-real | pass | 0 | None | 0 | 0/0 | 18406020 | 193876 | 0.193370808 |
| qs4-p1-real-20261007T180319Z.p1-real.r0 | p1-real | pass | 0 | None | 2 | 1/6 | 10738734 | 168015 | 0.152600604 |
| qs4-p2-real-20261007T180319Z.p2-real.r0 | p2-real | pass | 0 | None | 3 | 0/2 | 10319452 | 188014 | 0.157892280 |
| qs4-p3-real-20261007T180318Z.p3-real.r0 | p3-real | pass | 0 | None | 3 | 0/2 | 18478215 | 232635 | 0.219176418 |
| qs4-p1-real-20261007T182018Z.p1-real.r0 | p1-real | pass | 0 | None | 2 | 1/6 | 7354968 | 148305 | 0.129274728 |
| qs4-p4-real-20261007T182035Z.p4-real.r0 | p4-real | pass | 0 | None | 1 | 0/0 | 10149748 | 176078 | 0.155945160 |
| qs4-p3-planted-20261007T183213Z.p3-planted.r0 | p3-planted | fail | 1 | 1 | 1 | 0/2 | 5734637 | 71245 | 0.076619094 |
| qs4-p4-planted-20261007T183731Z.p4-planted.r0 | p4-planted | fail | 1 | 1 | 1 | 0/0 | 7158351 | 70109 | 0.081935298 |
| qs4-p5-planted-20261007T184116Z.p5-planted.r0 | p5-planted | pass | 2 | 2 | 2 | 1/5 | 8759596 | 75784 | 0.090063624 |
| qs4-p1-planted-20261007T184849Z.p1-planted.r0 | p1-planted | pass | 2 | 2 | 3 | 1/6 | 4246347 | 49755 | 0.056018874 |
| qs4-p2-planted-20261007T185343Z.p2-planted.r0 | p2-planted | pass | 2 | 2 | 2 | 0/3 | 4565837 | 60455 | 0.063886854 |
| qs4-p3-real-20261007T185534Z.p3-real.r0 | p3-real | pass | 0 | None | 3 | 0/2 | 14692165 | 223804 | 0.199330062 |
| qs4-p2-real-20261007T190528Z.p2-real.r0 | p2-real | pass | 0 | None | 0 | 0/2 | 11921626 | 172375 | 0.157849764 |
| qs4-p2-real-20261007T190152Z.p2-real.r0 | p2-real | pass | 0 | None | 4 | 1/2 | 11668337 | 229621 | 0.192249966 |
| qs4-p1-planted-20261007T192412Z.p1-planted.r0 | p1-planted | pass | 2 | 2 | 3 | 1/6 | 3854332 | 52541 | 0.056860320 |
| qs4-p2-planted-20261007T193024Z.p2-planted.r0 | p2-planted | pass | 2 | 2 | 4 | 1/3 | 5873936 | 88846 | 0.086774832 |
| qs4-p5-planted-20261007T192422Z.p5-planted.r0 | p5-planted | fail | 1 | 1 | 2 | 0/5 | 9926644 | 86450 | 0.102101160 |
| qs4-p3-planted-20261007T194126Z.p3-planted.r0 | p3-planted | fail | 1 | 1 | 1 | 0/2 | 10201144 | 78143 | 0.094281336 |
| qs4-p1-real-20261007T191814Z.p1-real.r0 | p1-real | pass | 0 | None | 0 | 0/6 | 12612727 | 298311 | 0.240211746 |
| qs4-p4-real-20261007T194018Z.p4-real.r0 | p4-real | pass | 0 | None | 1 | 0/0 | 12015675 | 247753 | 0.207324330 |
| qs4-p4-planted-20261007T195301Z.p4-planted.r0 | p4-planted | fail | 1 | 1 | 1 | 0/0 | 5962063 | 69940 | 0.075385002 |
| qs4-p5-real-20261007T202615Z.p5-real.r0 | p5-real | pass | 0 | None | 5 | 2/5 | 18713336 | 235880 | 0.224272656 |
| qs4-p3-real-20261007T202815Z.p3-real.r0 | p3-real | pass | 0 | None | 0 | 0/2 | 16306625 | 262536 | 0.229575894 |
| qs4-p5-real-20261007T203330Z.p5-real.r0 | p5-real | stopped | None | None | None | None/None | 25303385 | 275761 | 0.275417982 |

## QS4h

| run | item | status | verdict | plants caught, screen | plants caught, judged | findings | recorded in-view findings located | read | output | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| qs4h-h3-planted-20261008T061843Z.h3-planted.r0 | h3-planted | pass | NOT READY | 2 | 2 | 3 | 0/4 | 7403398 | 87706 | 0.186210024 |
| qs4h-h2-real-20261008T064206Z.h2-real.r0 | h2-real | pass | NOT READY | 0 | None | 1 | 1/4 | 13913265 | 200278 | 0.363491724 |
| qs4h-h2-planted-20261008T071425Z.h2-planted.r0 | h2-planted | fail | NOT READY | 1 | 2 | 3 | 2/4 | 7105017 | 92211 | 0.185193180 |
| qs4h-h1-planted-20261008T072238Z.h1-planted.r0 | h1-planted | fail | NOT READY | 1 | 2 | 3 | 6/6 | 10128096 | 128939 | 0.258499344 |
| qs4h-h4-planted-20261008T072239Z.h4-planted.r0 | h4-planted | pass | NOT READY | 2 | 2 | 4 | 1/5 | 13367486 | 101175 | 0.248108664 |
| qs4h-h2-planted-20261008T074514Z.h2-planted.r0 | h2-planted | fail | NOT READY | 1 | 2 | 3 | 2/4 | 5971426 | 117290 | 0.208780728 |
| qs4h-h3-real-20261008T073109Z.h3-real.r0 | h3-real | pass | NOT READY | 0 | None | 3 | 3/4 | 20221721 | 227362 | 0.445050540 |
| qs4h-h1-planted-20261008T080613Z.h1-planted.r0 | h1-planted | fail | NOT READY | 1 | 2 | 3 | 6/6 | 9776660 | 140588 | 0.267600048 |
| qs4h-h4-real-20261008T081708Z.h4-real.r0 | h4-real | pass | NOT READY | 0 | None | 2 | 1/5 | 15498103 | 151029 | 0.330141924 |
| qs4h-h4-planted-20261008T083057Z.h4-planted.r0 | h4-planted | pass | NOT READY | 2 | 2 | 3 | 1/5 | 11291722 | 120016 | 0.256723896 |
| qs4h-h3-planted-20261008T084817Z.h3-planted.r0 | h3-planted | pass | NOT READY | 2 | 2 | 2 | 0/4 | 8041672 | 108856 | 0.217471200 |
| qs4h-h2-planted-20261008T085947Z.h2-planted.r0 | h2-planted | pass | NOT READY | 2 | 2 | 4 | 2/4 | 6779445 | 127069 | 0.223431180 |
| qs4h-h3-planted-20261008T090652Z.h3-planted.r0 | h3-planted | pass | NOT READY | 2 | 2 | 2 | 0/4 | 6333525 | 92396 | 0.186119388 |
| qs4h-h1-planted-20261008T091648Z.h1-planted.r0 | h1-planted | pass | NOT READY | 2 | 2 | 3 | 6/6 | 11026780 | 140399 | 0.273239328 |
| qs4h-h4-planted-20261008T092139Z.h4-planted.r0 | h4-planted | pass | NOT READY | 2 | 2 | 4 | 1/5 | 17400007 | 122617 | 0.311433828 |
| qs4h-h1-planted-20261008T093401Z.h1-planted.r0 | h1-planted | pass | NOT READY | 2 | 2 | 3 | 6/6 | 8408270 | 118392 | 0.229347048 |
| qs4h-h3-planted-20261008T091310Z.h3-planted.r0 | h3-planted | fail | NOT READY | 1 | 1 | 3 | 2/4 | 21642808 | 189568 | 0.385038084 |
| qs4h-h2-planted-20261008T100959Z.h2-planted.r0 | h2-planted | fail | NOT READY | 1 | 2 | 3 | 2/4 | 6974913 | 136272 | 0.120215190 |
| qs4h-h4-real-20261008T100014Z.h4-real.r0 | h4-real | pass | NOT READY | 0 | None | 3 | 2/5 | 29380583 | 244331 | 0.267043746 |
| qs4h-h2-real-20261008T103332Z.h2-real.r0 | h2-real | pass | NOT READY | 0 | None | 4 | 0/4 | 11462890 | 224001 | 0.189257844 |
| qs4h-h1-real-20261008T104554Z.h1-real.r0 | h1-real | pass | NOT READY | 0 | None | 2 | 6/6 | 24771577 | 298331 | 0.281762094 |
| qs4h-h2-real-20261008T112631Z.h2-real.r0 | h2-real | pass | READY | 0 | None | 3 | 0/4 | 18986854 | 264633 | 0.237412572 |
| qs4h-h4-real-20261008T121314Z.h4-real.r0 | h4-real | pass | NOT READY | 0 | None | 3 | 1/5 | 20771874 | 156162 | 0.182134428 |
| qs4h-h3-real-20261008T115808Z.h3-real.r0 | h3-real | pass | NOT READY | 0 | None | 3 | 0/4 | 21483397 | 214347 | 0.221170230 |
| qs4h-h3-real-20261008T124335Z.h3-real.r0 | h3-real | pass | NOT READY | 0 | None | 1 | 0/4 | 21435094 | 287479 | 0.257634636 |
| qs4h-h4-real-20261008T130129Z.h4-real.r0 | h4-real | pass | NOT READY | 0 | None | 4 | 1/5 | 18616509 | 171442 | 0.185084910 |
| qs4h-h3-real-20261008T123944Z.h3-real.r0 | h3-real | pass | READY | 0 | None | 2 | 0/4 | 19123964 | 213157 | 0.209293536 |
| qs4h-h4-planted-20261008T132936Z.h4-planted.r0 | h4-planted | pass | NOT READY | 2 | 2 | 4 | 1/5 | 15396693 | 116815 | 0.143593590 |
| qs4h-h1-real-20261008T132917Z.h1-real.r0 | h1-real | pass | READY | 0 | None | 4 | 6/6 | 29149044 | 268009 | 0.272391696 |
| qs4h-h2-real-20261008T133933Z.h2-real.r0 | h2-real | pass | READY | 0 | None | 1 | 0/4 | 17274948 | 276803 | 0.240815712 |

## Batches

| batch | thinking | entered | runs | statuses | dropped attempts | read (hit/miss) | output | computed $ | billed $ | reconciliation | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| probe-20261006T192624Z | n/a | no | 0 | none | n/a | 0/0 | 0 | 0.00000225 | 0.00 | ok | no runs, so not named |
| qs1-20261006T215214Z | off | no | 105 | pass 105 | n/a | 106624/24845 | 7630 | 0.008626872 | 0.01 | ok | superseded: QS1 thinking off under 1.3765303639a2.8cf70454e2b7; QS1 ran again under the restated version (lead.md 20:33:53) |
| qs1-20261006T215607Z | on | no | 105 | fail 44, pass 46, refused 15 | n/a | 74112/18577 | 13036 | 0.010832736 | 0.00 | ok | superseded: QS1's assertion that reasoning be present overreached D8 (lead.md 15:00:40) |
| qs1-20261007T000146Z | on | no | 105 | pass 90, refused 15 | n/a | 100992/24429 | 13676 | 0.012175176 | 0.01 | ok | superseded: QS1 thinking on under 1.3765303639a2.e84c86f722e2; QS1 ran again under the restated version (lead.md 20:33:53) |
| qs6-c016k-20261007T012012Z | off | yes | 66 | pass 66 | n/a | 1131520/30608 | 8297 | 0.025932420 | 0.02 | ok | QS6 c016k, thinking off, complete |
| qs6-c016k-20261007T012554Z | on | yes | 66 | pass 66 | n/a | 1131520/32258 | 40412 | 0.064965420 | 0.03 | mismatch | QS6 c016k, thinking on, complete; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-c032k-20261007T015103Z | off | yes | 66 | pass 66 | n/a | 2144366/27562 | 9860 | 0.032971296 | 0.02 | ok | QS6 c032k, thinking off, complete |
| qs6-c032k-20261007T015555Z | on | yes | 66 | pass 66 | n/a | 2144768/28810 | 43641 | 0.073885308 | 0.03 | mismatch | QS6 c032k, thinking on, complete; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-c064k-20261007T020307Z | off | no | 27 | error 1, pass 26 | n/a | 1641856/37013 | 1852 | 0.023181936 | 0.02 | ok | stopped after 27 runs: a request closed with no reply, before the retry (lead.md 19:11:24) |
| qs6-c064k-20261007T020712Z | on | no | 4 | error 1, pass 3 | n/a | 161408/32365 | 434 | 0.011203248 | 0.00 | ok | stopped after 4 runs: a request closed with no reply, before the retry (lead.md 19:11:24) |
| probe-20261007T025020Z | n/a | no | 0 | none | 0 | 0/0 | 0 | 0.0000045 | 0.00 | ok | no runs, so not named |
| qs6-c064k-20261007T025049Z | off | yes | 66 | pass 66 | 0 | 4248832/12788 | 9244 | 0.040426692 | 0.02 | mismatch | QS6 c064k, thinking off, complete; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-c064k-20261007T025612Z | on | no | 43 | error 1, pass 42 | 3 | 2704128/8964 | 8680 | 0.029334468 | 0.01 | ok | stopped after 43 runs, at its third request closed with no reply (lead.md 20:01:46) |
| qs6-c128k-20261007T030203Z | off | no | 46 | error 1, pass 45 | 3 | 6180608/84820 | 4528 | 0.067967748 | 0.03 | mismatch | stopped after 46 runs, at its third request closed with no reply (lead.md 20:07:50) |
| qs6-c128k-20261007T030758Z | off | yes | 66 | pass 66 | 4 | 9174528/14652 | 9574 | 0.070936068 | 0.04 | mismatch | QS6 c128k, thinking off, complete at --max-unmetered 15; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-c128k-20261007T031458Z | on | yes | 66 | pass 66 | 3 | 9100416/90414 | 24055 | 0.110597196 | 0.05 | mismatch | QS6 c128k, thinking on, complete at --max-unmetered 15; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-whole-20261007T032238Z | off | yes | 66 | fail 1, pass 65 | 6 | 10148096/27850 | 9703 | 0.080891676 | 0.04 | mismatch | QS6 whole ledger, thinking off, complete at --max-unmetered 15; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-whole-20261007T033052Z | on | yes | 66 | pass 66 | 0 | 10148096/29500 | 23168 | 0.097544676 | 0.05 | mismatch | QS6 whole ledger, thinking on, complete at --max-unmetered 15; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs6-c064k-20261007T033726Z | on | yes | 66 | pass 66 | 3 | 4249344/13926 | 42668 | 0.080879964 | 0.04 | mismatch | QS6 c064k, thinking on, complete at --max-unmetered 15; billed at about half; a holiday is believed (lead.md 18:35:19) |
| qs1-20261007T034705Z | off | yes | 105 | pass 105 | 0 | 107008/24330 | 7586 | 0.017048748 | 0.00 | ok | QS1, thinking off, complete, under QS1 1.3765303639a2.2ff54c82d6f4 (lead.md 20:33:53) |
| qs1-20261007T035043Z | on | yes | 105 | pass 90, refused 15 | 0 | 100864/24443 | 14237 | 0.025026984 | 0.01 | ok | QS1, thinking on, effort high, complete, under QS1 1.3765303639a2.2ff54c82d6f4 (lead.md 20:33:53) |
| qs4-p2-planted-20261007T100101Z | on | no | 1 | error 1 | 0 | 1664/3326 | 237 | 0.000648342 | 0.00 | ok | refused by DeepSeek's content filter (HTTP 400) at its third request, after read_file returned round 6's verifier brief (lead.md 03:03:45) |
| qs4-p2-planted-20261007T100330Z | on | no | 1 | pass 1 | 5 | 4358652/110926 | 81392 | 0.078552306 | 0.06 | ok | completed under read_file's earlier, cat -n form, before db94d41; reported apart, not scored (lead.md 03:15:00, 03:23:16) |
| qs4-p2-real-20261007T101508Z | on | no | 1 | error 1 | 0 | 2816/1978 | 240 | 0.000451398 | 0.01 | ok | refused by DeepSeek's content filter the same way (lead.md 03:18:10) |
| diag-filter-20261007T101811Z | on | no | 7 | fail 4, pass 3 | 0 | 2304/15138 | 192 | 0.002395062 | 0.00 | ok | a diagnostic of DeepSeek's content filter, not a suite (lead.md 03:23:16) |
| diag-filter2-20261007T102020Z | on | no | 4 | fail 1, pass 3 | 0 | 3968/3882 | 192 | 0.000711654 | 0.00 | ok | a diagnostic of DeepSeek's content filter, not a suite (lead.md 03:23:16) |
| qs4-p2-planted-20261007T103409Z | on | yes | 1 | fail 1 | 2 | 4089472/112335 | 67573 | 0.069664716 | 0.06 | ok | QS4 p2-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p2-real-20261007T104245Z | on | no | 1 | error 1 | 10 | 10350976/116325 | 229064 | 0.185942328 | 0.18 | ok | stopped at its tenth request closed with no reply, the batch's allowance (lead.md 04:05:06) |
| qs4-p2-real-20261007T110448Z | on | yes | 1 | pass 1 | 13 | 9067264/116907 | 184155 | 0.155233092 | 0.15 | ok | QS4 p2-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p1-planted-20261007T112510Z | on | yes | 1 | pass 1 | 2 | 5488768/110695 | 67862 | 0.073790004 | 0.08 | ok | QS4 p1-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p1-real-20261007T113404Z | on | yes | 1 | pass 1 | 19 | 27085824/200128 | 215133 | 0.240358722 | 0.25 | ok | QS4 p1-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p3-planted-20261007T120601Z | on | yes | 1 | pass 1 | 2 | 6315264/121865 | 62724 | 0.074862192 | 0.07 | ok | QS4 p3-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p3-real-20261007T121519Z | on | yes | 1 | pass 1 | 11 | 18334976/151721 | 217297 | 0.208143528 | 0.21 | ok | QS4 p3-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p4-planted-20261007T125519Z | on | yes | 1 | pass 1 | 2 | 5739776/117037 | 70361 | 0.076993728 | 0.06 | ok | QS4 p4-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p4-real-20261007T130515Z | on | yes | 1 | pass 1 | 4 | 12907904/141846 | 215322 | 0.189196062 | 0.20 | ok | QS4 p4-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p5-planted-20261007T132806Z | on | yes | 1 | pass 1 | 9 | 12596096/177435 | 100537 | 0.124727988 | 0.11 | ok | QS4 p5-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p5-real-20261007T134511Z | on | yes | 1 | stopped 1 | 11 | 39944576/231813 | 269875 | 0.316532928 | 0.30 | ok | QS4 p5-real, pass 1: stopped at the 40,000,000-token prompt cap, with no report; shown, not scored (lead.md 07:19:30) |
| qs4-p3-planted-20261007T142258Z | on | yes | 1 | pass 1 | 4 | 5763840/101718 | 99527 | 0.092267670 | 0.08 | ok | QS4 p3-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p4-planted-20261007T143555Z | on | yes | 1 | fail 1 | 4 | 7148928/131529 | 98425 | 0.100233384 | 0.09 | ok | QS4 p4-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p3-real-20261007T144815Z | on | no | 1 | error 1 | 14 | 24929792/167590 | 265118 | 0.259000926 | 0.25 | ok | ended by one call closed with no reply three times running (lead.md 08:57:42) |
| qs4-p5-real-20261007T151656Z | on | yes | 1 | pass 1 | 11 | 26345344/219458 | 249560 | 0.261692982 | 0.27 | ok | QS4 p5-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p1-real-20261007T154444Z | on | no | 1 | error 1 | 5 | 7205760/139873 | 116151 | 0.112291080 | 0.12 | ok | ended by one call closed with no reply three times running (lead.md 08:57:42) |
| qs4-p1-planted-20261007T155708Z | on | yes | 1 | pass 1 | 6 | 4780800/97604 | 52508 | 0.060490050 | 0.05 | ok | QS4 p1-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p5-planted-20261007T160649Z | on | yes | 1 | fail 1 | 4 | 10527104/148981 | 84890 | 0.104864712 | 0.10 | ok | QS4 p5-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p2-planted-20261007T161904Z | on | yes | 1 | pass 1 | 8 | 5456256/108243 | 60956 | 0.069181068 | 0.08 | ok | QS4 p2-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p4-real-20261007T163001Z | on | yes | 1 | pass 1 | 21 | 18257536/148484 | 193876 | 0.193373058 | 0.19 | ok | QS4 p4-real: reported, pass; scored by the lead's judgement, checked by verifier-J (alone) |
| qs4-p1-real-20261007T170750Z | on | no | 1 | pass 1 | 5 | 12087552/133740 | 156449 | 0.150195306 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p3-real-20261007T170750Z | on | no | 1 | pass 1 | 5 | 9346048/121299 | 197139 | 0.164518644 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p2-real-20261007T170750Z | on | no | 1 | pass 1 | 11 | 7660800/119045 | 145337 | 0.128043600 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p1-real-20261007T172454Z | on | no | 1 | pass 1 | 6 | 6060672/131108 | 83585 | 0.088001466 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p4-real-20261007T173035Z | on | no | 1 | pass 1 | 4 | 9398016/150249 | 133484 | 0.130824048 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p3-planted-20261007T172638Z | on | no | 1 | fail 1 | 18 | 12321920/144252 | 177040 | 0.164829810 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p5-planted-20261007T174903Z | on | no | 1 | pass 1 | 4 | 5221248/132910 | 63030 | 0.073420494 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p4-planted-20261007T174423Z | on | no | 1 | fail 1 | 8 | 5464064/136167 | 56839 | 0.070922892 | None | concurrent | a lane run whose outside sources were unreadable in the sandbox (EIO), at the lanes' first path (lead.md 11:03:35) |
| qs4-p1-real-20261007T180319Z | on | yes | 1 | pass 1 | 8 | 10605568/133166 | 168015 | 0.152602854 | None | concurrent | QS4 p1-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p2-real-20261007T180319Z | on | yes | 1 | pass 1 | 6 | 10223360/96092 | 188014 | 0.157894530 | None | concurrent | QS4 p2-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p3-real-20261007T180318Z | on | yes | 1 | pass 1 | 14 | 18313856/164359 | 232635 | 0.219178668 | None | concurrent | QS4 p3-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p1-real-20261007T182018Z | on | yes | 1 | pass 1 | 6 | 7230976/123992 | 148305 | 0.129276978 | None | concurrent | QS4 p1-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p4-real-20261007T182035Z | on | yes | 1 | pass 1 | 8 | 10014720/135028 | 176078 | 0.155947410 | None | concurrent | QS4 p4-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p3-planted-20261007T183213Z | on | yes | 1 | fail 1 | 4 | 5621248/113389 | 71245 | 0.076621344 | None | concurrent | QS4 p3-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p4-planted-20261007T183731Z | on | yes | 1 | fail 1 | 7 | 7033216/125135 | 70109 | 0.081937548 | None | concurrent | QS4 p4-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p5-planted-20261007T184116Z | on | yes | 1 | pass 1 | 11 | 8635008/124588 | 75784 | 0.090065874 | None | concurrent | QS4 p5-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p1-planted-20261007T184849Z | on | yes | 1 | pass 1 | 3 | 4155008/91339 | 49755 | 0.056021124 | None | concurrent | QS4 p1-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p2-planted-20261007T185343Z | on | yes | 1 | pass 1 | 4 | 4471168/94669 | 60455 | 0.063889104 | None | concurrent | QS4 p2-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p5-real-20261007T183548Z | on | no | 1 | error 1 | 23 | 18813440/177164 | 166173 | 0.182720970 | None | concurrent | ended at the batch's allowance of 23 attempts closed with no reply, at turn 113 of 136 attempts; run again by its lane (lead.md 13:26:42) |
| qs4-p3-real-20261007T185534Z | on | yes | 1 | pass 1 | 13 | 14549504/142661 | 223804 | 0.199332312 | None | concurrent | QS4 p3-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p2-real-20261007T190528Z | on | yes | 1 | pass 1 | 11 | 11794688/126938 | 172375 | 0.157852014 | None | concurrent | QS4 p2-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p2-real-20261007T190152Z | on | yes | 1 | pass 1 | 12 | 11535872/132465 | 229621 | 0.192252216 | None | concurrent | QS4 p2-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p1-planted-20261007T192412Z | on | yes | 1 | pass 1 | 1 | 3760640/93692 | 52541 | 0.056862570 | None | concurrent | QS4 p1-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p2-planted-20261007T193024Z | on | yes | 1 | pass 1 | 4 | 5766144/107792 | 88846 | 0.086777082 | None | concurrent | QS4 p2-planted: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p5-planted-20261007T192422Z | on | yes | 1 | fail 1 | 4 | 9787520/139124 | 86450 | 0.102103410 | None | concurrent | QS4 p5-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p3-planted-20261007T194126Z | on | yes | 1 | fail 1 | 7 | 10086912/114232 | 78143 | 0.094283586 | None | concurrent | QS4 p3-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p1-real-20261007T191814Z | on | yes | 1 | pass 1 | 20 | 12453632/159095 | 298311 | 0.240213996 | None | concurrent | QS4 p1-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p4-real-20261007T194018Z | on | yes | 1 | pass 1 | 6 | 11861760/153915 | 247753 | 0.207326580 | None | concurrent | QS4 p4-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p4-planted-20261007T195301Z | on | yes | 1 | fail 1 | 1 | 5856384/105679 | 69940 | 0.075387252 | None | concurrent | QS4 p4-planted: reported, fail; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p5-real-20261007T200042Z | on | no | 1 | error 1 | 23 | 21647744/193322 | 174817 | 0.198833982 | None | concurrent | ended at the batch's allowance of 23 attempts closed with no reply, at turn 118 of 141 attempts; run once more at an allowance of 35 (lead.md 13:26:42) |
| qs4-p3-real-20261007T200155Z | on | no | 1 | error 1 | 23 | 16252800/159141 | 205433 | 0.195891600 | None | concurrent | ended at the batch's allowance of 23 attempts closed with no reply, at turn 102 of 125 attempts; run again by its lane |
| qs4-p5-real-20261007T195306Z | on | no | 1 | error 1 | 23 | 24346240/219423 | 292830 | 0.281652420 | None | concurrent | ended at the batch's allowance of 23 attempts closed with no reply; run again at an allowance of 35 (lead.md 13:33:50) |
| qs4-p5-real-20261007T202615Z | on | yes | 1 | pass 1 | 14 | 18532352/180984 | 235880 | 0.224274906 | None | concurrent | QS4 p5-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p3-real-20261007T202815Z | on | yes | 1 | pass 1 | 12 | 16149248/157377 | 262536 | 0.229578144 | None | concurrent | QS4 p3-real: reported, pass; scored by the lead's judgement, checked by verifier-J (concurrent, in a lane) |
| qs4-p5-real-20261007T203330Z | on | yes | 1 | stopped 1 | 17 | 25071744/231641 | 275761 | 0.275420232 | None | concurrent | QS4 p5-real, pass 4: stopped at the per-call cap, a request of about 901,532 tokens past 900,000, with no report; shown, not scored |
| probe-20261007T210718Z | n/a | no | 0 | none | 0 | 0/0 | 0 | 0.00000225 | 0.00 | ok | no runs, so not named |
| probe-20261008T014643Z | n/a | no | 0 | none | 0 | 0/0 | 0 | 0.0000045 | 0.00 | ok | no runs, so not named |
| qs4h-h3-planted-20261008T061843Z | on | yes | 1 | pass 1 | 13 | 7279104/124294 | 87706 | 0.186214524 | 0.19 | ok | QS4h h3-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (alone) |
| qs4h-h2-real-20261008T064206Z | on | yes | 1 | pass 1 | 22 | 13778304/134961 | 200278 | 0.363496224 | None | concurrent | QS4h h2-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-real-20261008T064206Z | on | no | 1 | error 1 | 26 | 22466432/153090 | 266866 | 0.500969292 | None | concurrent | ended by a connection reset (WinError 10054) at turn 132 of 159 attempts; P0 retries only a close with no reply (lead.md 00:22:06) |
| qs4h-h4-real-20261008T064206Z | on | no | 1 | error 1 | 28 | 18891264/186639 | 152306 | 0.352110984 | None | concurrent | ended at the batch's allowance of 28 attempts closed with no reply, at turn 114 of 142 attempts, at peak (lead.md 00:22:06) |
| qs4h-h2-planted-20261008T071425Z | on | yes | 1 | fail 1 | 12 | 6996480/108537 | 92211 | 0.185197680 | None | concurrent | QS4h h2-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-planted-20261008T072238Z | on | yes | 1 | fail 1 | 14 | 9981824/146272 | 128939 | 0.258503844 | None | concurrent | QS4h h1-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-planted-20261008T072239Z | on | yes | 1 | pass 1 | 20 | 13209344/158142 | 101175 | 0.248113164 | None | concurrent | QS4h h4-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h2-planted-20261008T074514Z | on | yes | 1 | fail 1 | 9 | 5861888/109538 | 117290 | 0.208785228 | None | concurrent | QS4h h2-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-real-20261008T073109Z | on | yes | 1 | pass 1 | 26 | 20048640/173081 | 227362 | 0.445055040 | None | concurrent | QS4h h3-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-planted-20261008T080613Z | on | yes | 1 | fail 1 | 18 | 9639808/136852 | 140588 | 0.267604548 | None | concurrent | QS4h h1-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-real-20261008T075642Z | on | no | 1 | error 1 | 40 | 22402688/152299 | 245173 | 0.474317928 | None | concurrent | ended at the batch's allowance of 40 attempts closed with no reply, at turn 122 of 162 attempts, at peak (lead.md 01:47:15) |
| qs4h-h4-real-20261008T081708Z | on | yes | 1 | pass 1 | 24 | 15307904/190199 | 151029 | 0.330146424 | None | concurrent | QS4h h4-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-planted-20261008T083057Z | on | yes | 1 | pass 1 | 17 | 11138816/152906 | 120016 | 0.256728396 | None | concurrent | QS4h h4-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-planted-20261008T084817Z | on | yes | 1 | pass 1 | 8 | 7910400/131272 | 108856 | 0.217475700 | None | concurrent | QS4h h3-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-planted-20261008T084817Z | on | no | 1 | error 1 | 19 | 15743616/170868 | 114045 | 0.282580596 | None | concurrent | ended by a connection reset (WinError 10054) at turn 106 of 126 attempts, at peak; P0 retries only a close with no reply |
| qs4h-h2-planted-20261008T085947Z | on | yes | 1 | pass 1 | 6 | 6676480/102965 | 127069 | 0.223435680 | None | concurrent | QS4h h2-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-planted-20261008T090652Z | on | yes | 1 | pass 1 | 3 | 6206848/126677 | 92396 | 0.186123888 | None | concurrent | QS4h h3-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-planted-20261008T091648Z | on | yes | 1 | pass 1 | 5 | 10895488/131292 | 140399 | 0.273243828 | None | concurrent | QS4h h1-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-planted-20261008T092139Z | on | yes | 1 | pass 1 | 9 | 17196288/203719 | 122617 | 0.311438328 | None | concurrent | QS4h h4-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-planted-20261008T093401Z | on | yes | 1 | pass 1 | 6 | 8283008/125262 | 118392 | 0.229351548 | None | concurrent | QS4h h1-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-planted-20261008T091310Z | on | yes | 1 | fail 1 | 23 | 21448832/193976 | 189568 | 0.385042584 | None | concurrent | QS4h h3-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h2-planted-20261008T100959Z | on | yes | 1 | fail 1 | 6 | 6855680/119233 | 136272 | 0.120217440 | None | concurrent | QS4h h2-planted: reported, fail; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-real-20261008T100014Z | on | yes | 1 | pass 1 | 27 | 29160832/219751 | 244331 | 0.267045996 | None | concurrent | QS4h h4-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h2-real-20261008T103332Z | on | yes | 1 | pass 1 | 23 | 11323648/139242 | 224001 | 0.189260094 | None | concurrent | QS4h h2-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-real-20261008T100017Z | on | no | 1 | error 1 | 35 | 16959616/142965 | 184208 | 0.182850648 | None | concurrent | ended by one request closed with no reply five times running, its retries spent, at turn 101 of 136 attempts, off-peak; h1-real's second loss, not run again |
| qs4h-h1-real-20261008T104554Z | on | yes | 1 | pass 1 | 29 | 24578048/193529 | 298331 | 0.281764344 | None | concurrent | QS4h h1-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-real-20261008T110550Z | on | no | 1 | error 1 | 39 | 21280384/172918 | 256344 | 0.243587502 | None | concurrent | ended by one request closed with no reply five times running, its retries spent, at turn 109 of 148 attempts, off-peak; h1-real's third loss, not run again (lead.md 05:00:45) |
| qs4h-h2-real-20261008T112631Z | on | yes | 1 | pass 1 | 22 | 18839424/147430 | 264633 | 0.237414822 | None | concurrent | QS4h h2-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h2-real-20261008T113521Z | on | no | 1 | error 1 | 40 | 24327424/159412 | 282294 | 0.266272722 | None | concurrent | ended at the batch's allowance of 40 attempts closed with no reply, at turn 121 of 161 attempts, off-peak; run once more at 45 |
| qs4h-h4-real-20261008T121314Z | on | yes | 1 | pass 1 | 20 | 20594176/177698 | 156162 | 0.182136678 | None | concurrent | QS4h h4-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-real-20261008T115808Z | on | yes | 1 | pass 1 | 19 | 21292160/191237 | 214347 | 0.221172480 | None | concurrent | QS4h h3-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-real-20261008T124335Z | on | yes | 1 | pass 1 | 19 | 21293312/141782 | 287479 | 0.257636886 | None | concurrent | QS4h h3-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-real-20261008T130129Z | on | yes | 1 | pass 1 | 11 | 18437120/179389 | 171442 | 0.185087160 | None | concurrent | QS4h h4-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h3-real-20261008T123944Z | on | yes | 1 | pass 1 | 20 | 18960512/163452 | 213157 | 0.209295786 | None | concurrent | QS4h h3-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h4-planted-20261008T132936Z | on | yes | 1 | pass 1 | 10 | 15210880/185813 | 116815 | 0.143595840 | None | concurrent | QS4h h4-planted: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h1-real-20261008T132917Z | on | yes | 1 | pass 1 | 34 | 28984832/164212 | 268009 | 0.272393946 | None | concurrent | QS4h h1-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| qs4h-h2-real-20261008T133933Z | on | yes | 1 | pass 1 | 11 | 17119104/155844 | 276803 | 0.240817962 | None | concurrent | QS4h h2-real: reported, pass; scored by the lead's judgement, checked by verifier-JH (concurrent, in a lane) |
| probe-20261008T145303Z | n/a | no | 0 | none | 0 | 0/0 | 0 | 0.00000225 | 0.00 | ok | no runs, so not named |
| probe-20261008T152454Z | n/a | no | 0 | none | 0 | 0/0 | 0 | 0.00000225 | 0.00 | ok | no runs, so not named |

Computed over every live batch with a summary line: $18.777486312. A batch interrupted before its summary is in the spend file only. Billed figures are the balance's, to two decimals; the usage export is the authority.

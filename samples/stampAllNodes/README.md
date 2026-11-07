# What is this?
This is a sample program that verifies whether multiple participating nodes are actually performing distributed processing.

When you run the phase stampAllNodes.main defined in stamp.py,
it creates an empty file named `AgenTalk_stamp_YYYYmmdd_HHMMSS.txt` in /tmp on each participating node.

The `YYYYmmdd_HHMMSS` portion is replaced with the date and time
(year, month, day, hour, minute, second) of execution.

# How to run
As with the other sample programs, run `agt reg .` in this directory, samples/stampAllNodes.

Then run:

```bash
agt run stampAllNodes.main
```

This will create the file in /tmp on all nodes.

Since execution requires one ticket, please add a ticket beforehand by running:

```bash
agt at
```


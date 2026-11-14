# What is this?
This sample program demonstrates how MapReduce-style processing
(or scatter-gather processing) can be implemented using AgenTalk.

The `worker` Phases perform distributed processing,
while the `gather` Phase collects and combines their results.

# How to Run
Start a Reactor using `agt start .`, as described in the `helloReactor` example.
Then register the `entry`, `worker`, and `gather` Phases by running:

```bash
agt reg .
```

Next, execute the `entry` Phase:

```bash
agt run mapReduce.entry
```

# Processing in the worker Phase
In this sample program, the values from 1 to 10 are distributed among the `worker` Phases.

Each `worker` Phase simply passes its assigned value to the `gather` Phase without modification.

The actual exchange of values takes place through a Redis server accessible from all AgenTalk nodes.
In AgenTalk, this Redis server is referred to as **Global Redis**.

# Processing in the gather Phase
The `gather` Phase receives the values reported by the `worker` Phases one by one and calculates their sum.

Once all `worker` Phases have reported their values,
the `gather` Phase prints the total sum to the terminal running the Reactor and then terminates.


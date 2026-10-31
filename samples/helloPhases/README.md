# What is this?
AgenTalk allows you to register multiple Phases.
This sample program registers three Phases: `Ready`, `Set`, and `Go`.
The `Ready` Phase invokes `Set`, which in turn invokes `Go`.

The actual Phase names are:

- `helloPhases.Ready`
- `helloPhases.Set`
- `helloPhases.Go`

The `act` function of a Phase can also accept arguments.
These arguments can be specified after the Phase name in the `agt run` command.

For example:

```bash
agt run helloPhases.Ready 3
```

This passes the argument `3` to the `helloPhases.Ready` Phase, effectively invoking its `act` function as `act(3)`.

# How to Run
Start a Reactor using `agt start`, as described in the `helloReactor` example.
Then register the `Ready`, `Set`, and `Go` Phases by running:

```bash
agt reg .
```

Next, execute the `Ready` Phase:

```bash
agt run helloPhases.Ready
```

The `Ready` Phase invokes `Set`, which in turn invokes `Go`.
As in the `helloReactor` example, each Phase prints a message, such as `Ready`, to the terminal running the Reactor.

To demonstrate passing an argument to the `act` function, run:

```bash
agt run helloPhases.Ready 3
```

This executes the sequence of `Ready`, `Set`, and `Go` three times.


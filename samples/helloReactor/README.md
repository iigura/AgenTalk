# What Is This?

This is the simplest AgenTalk sample program.
It displays the string `HELLO` in the Reactor terminal.

# How to Run
## Prerequisites
Follow the instructions in the README.md at the root of the AgenTalk repository to install AgenTalk in editable mode.
Make sure the Redis and Ray servers are also running.

## Start the Reactor
Start the Reactor by running:

```bash
agt start
```

## Register the `greet` Phase
Open another terminal, separate from the one running the Reactor.
From the `helloReactor` directory, run:

```bash
agt reg .
```

**Don't forget the period (`.`) after `reg`.**

If registration succeeds, the following message will appear in the Reactor terminal:

```text
Phase 'helloReactor.greet' is loaded.
```

## Run the `helloReactor.greet` Phase
Run:

```bash
agt run helloReactor.greet
```

At this point, however, you probably won't see `HELLO` in the Reactor terminal yet.

In AgenTalk, Phases generally use a ticket-based execution system.
A Phase will not execute unless it can acquire a ticket.

Issue a ticket for `helloReactor.greet` by running:

```bash
agt at
```

Once a ticket is issued, `HELLO` will appear in the Reactor terminal.

Tickets remain available until you clear them with:

```bash
agt cl
```

You can check the number of remaining tickets with:

```bash
agt ct
```


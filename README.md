# AgenTalk
Easy to develop with. Easy to scale.
An AI agent framework for local LLMs.

With the provided set of functions, you can quickly assemble processing workflows,
and scale them out at runtime via parallel and distributed execution powered by Ray.
AgenTalk coordinates with "Reactor" (which dispatches tasks) through Redis,
and by inserting deterministic validation steps along the way,
you can build robust workflows while keeping AI agents under system control.

Don't just hand everything off to AI.
You can develop and build AI agents with built-in validation and control,
so you can operate them with confidence.

Note: This project is in the early stages of public release, so the API and internal architecture may change.

## License
This project is licensed under the MIT License.
See `LICENSE` for details.

## Installation (editable install)
Install AgenTalk in editable mode for development.
From the root of this repository, run:

```bash
pip install -r requirements.txt
pip install -e .
```

`requirements.txt` installs the following packages:

* redis, ray, pyyaml, asttokens, ollama, dateparser, pdfminer.six

To verify the installation, run `import AgenTalk` in a Python interpreter.
If no error is raised, the installation was successful.

## Usage
For details, see the README in `samples/fitText`.

## Runtime setup (distributed execution setup)
Install AgenTalk on **all** nodes.
Since AgenTalk uses Ray, it is recommended to keep the Python version consistent across all nodes.

### Redis
AgenTalk uses Redis. On Linux, run:

```bash
sudo apt install redis
```

so that the Redis server can be started.

Next, start `redis-server`:

```bash
redis-server --port 6789 &
```

To confirm it is running correctly, use the following command
(you should get `PONG` back):

```bash
redis-cli -p 6789 ping
```

### Ray
#### Starting the head node
On the head node environment, start the Ray head node:

```bash
ray start --head
```

If it starts successfully, the command returns to the shell prompt.
Then run:

```bash
ray status
```

to check the status of the Ray cluster.

#### Joining remote nodes
To join the current session to the Ray head node, run:

```bash
ray start --address='HEAD_NODE_IP_ADDRESS:6379'
```

In particular, during development, if you want to join another session on the same machine
as a "remote node", run:

```bash
ray start --address='127.0.0.1:6379'
```

You can also check the join status with:

```bash
ray status
```

If `active` shows two `node_...` entries, a remote node has been added.
(When only the head node is running, there will be just one node listed under `active`.)

### Starting the reactor
From a shell on the terminal responsible for the head node, run:

```bash
agt start
```

### Registering tickets
On the remote node(s) that execute tasks, register as many "tickets" as the number of
tasks you want to run concurrently.
If you use a local LLM, decide the number of tickets while considering GPU memory usage
(if you’re unsure, start by registering just one ticket).

* `agt cl` clears tickets (sets the ticket count to 0)
* `agt at` adds one ticket (at = add ticket)
* `agt ct` shows the current ticket count (ct = count ticket)

For more details, run `agt help`.

### Registering Phases
Phases are registered using `agt reg`.
For details, see the README in `samples/fitText`.

### Running Phases
You can notify the reactor to run Phases via `agt run`.
For details, run `agt help` and see the description for `agt run`.

### Shutdown
Press Ctrl-C for the Reactor running on the head node,
or run the following command on a remote node:

```bash
agt stop
```


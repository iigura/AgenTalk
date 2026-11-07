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

* redis, ray, pyyaml, asttokens, ollama, dateparser, pdfminer.six, chardet

To verify the installation, run `import AgenTalk` in a Python interpreter.
If no error is raised, the installation was successful.

## Usage
For details, see the README in `samples/fitText`.
Additionally, you can find brief descriptions for examples
such as `helloReactor` and `helloPhases` in the `samples` directory;
please refer to them for further information.

## Runtime setup (distributed execution setup)
Install AgenTalk on **all** nodes.
Since AgenTalk uses Ray, it is recommended to keep the Python version consistent across all nodes.

### Redis
AgenTalk uses Redis.
On Ubuntu or similar Linux distributions, you can install Redis with:

```bash
sudo apt install redis
```

On Ubuntu, installing Redis may automatically start the Redis service,
which listens on the default port 6379.
Since this port conflicts with Ray's default port,
you should stop the service and disable its automatic startup if no other applications depend on it.

```
sudo systemctl disable --now redis-server
```

if Redis is already using port 6379,
the command above should stop the service and release the port immediately.
No system reboot is required.

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

### Using Multiple Computers (with Tailscale)
When running AgenTalk across multiple computers,
Ray and Redis must be configured to accept connections from other machines.

The following example uses Tailscale.
All computers are assumed to have Tailscale installed and to be connected to the same tailnet.

#### Tailscale Access Control
Communication between nodes must be permitted by Tailscale ACLs / Grants.

Redis uses TCP port 6789, while Ray's GCS uses TCP port 6379 by default.
However, Ray also uses additional ports for communication between nodes.

For example, to allow TCP communication between two trusted computers,
open the JSON editor under Access controls in the Tailscale admin console
and add the following rule to the existing `grants` array:

```json
{
    "src": ["HEAD_NODE_IP", "REMOTE_NODE_IP"],
    "dst": ["HEAD_NODE_IP", "REMOTE_NODE_IP"],
    "ip": ["tcp:*"]
}
```

Replace `HEAD_NODE_IP` and `REMOTE_NODE_IP` with the respective Tailscale IP addresses.

This configuration allows bidirectional TCP communication on all ports between the two specified computers.
Since some of Ray's internal communication ports may be assigned dynamically,
this example is intended to simplify experimental setups.

Note that this also allows access to other TCP services on these computers,
so use it only between trusted nodes.
For production environments, it is recommended to explicitly configure Ray's communication ports
and allow access only to the required ports.

#### Starting Redis
Start Redis on the head node.

Specify both the loopback address and the Tailscale IP address so that Redis can accept connections from other computers.

```bash
redis-server \
  --port 6789 \
  --bind 127.0.0.1 "$(tailscale ip -4)" \
  --protected-mode no &
```

If Redis is already running on port 6789,
make sure that stopping it will not affect any required data
or ongoing operations before restarting it with the settings above.

```bash
redis-cli -p 6789 shutdown
```

The configuration above is intended for experimental use with trusted Tailscale nodes only.
Since Redis authentication is not configured,
avoid exposing Redis to untrusted networks.
For long-term operation, consider enabling authentication using Redis ACLs or other appropriate mechanisms.

You can verify the connection from a remote node by running:

```bash
redis-cli -h HEAD_NODE_HOST -p 6789 ping
```

Replace `HEAD_NODE_HOST` with the hostname or IP address of the head node.

If Redis responds with `PONG`, the connection is working correctly.

#### Starting Ray
On the head node, start Ray by explicitly specifying its Tailscale IP address.

```bash
ray start --head --node-ip-address=$(tailscale ip -4)
```

On a remote node, join the Ray cluster by running:

```bash
ray start \
  --address=HEAD_NODE_HOST:6379 \
  --node-ip-address=$(tailscale ip -4)
```

Replace `HEAD_NODE_HOST` with the hostname or IP address of the head node.

You can check which nodes have joined the cluster by running the following command on the head node:

```bash
ray status
```

#### Configuring AgenTalk
On each computer, specify the Ray and Redis connection addresses in `config.yaml`.

For example, with the configuration described above, use:

```yaml
rayHeadNodeAddress: HEAD_NODE_HOST:6379
talkChannel:        redis://HEAD_NODE_HOST:6789/0
```

Replace `HEAD_NODE_HOST` with the hostname or IP address of the head node.

Make sure that all nodes connect to the same Ray cluster and Redis server.

Once the configuration is complete, start the Reactor on the head node by running `agt start`.

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


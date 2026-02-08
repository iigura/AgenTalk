```
filename: README.md
title: about fitText
author: Koji Iigura
```

# fitText
## What is fitText?
fitText demonstrates event-driven, constraint-aware text generation
that fits strict character-length and keyword requirements using a local LLM.
It is triggered by external events and performs a stepwise document generation process,
verifying the output and rewriting it as needed.

## How it works
When a `.json` file is added to the `gate` directory,
this event triggers the `fitText.firstDraft` phase.

Detection of the addition of a `.json` file is independent of AgenTalk.
This responsibility is handled by `gateToAgenTalk.py`.
The `fitText.firstDraft` phase is started by calling
the `AgenTalk.newSession()` function followed by the `invoke()` method.
`gateToAgenTalk.py` merely invokes AgenTalk’s public interfaces
and is not a component embedded within AgenTalk itself.

In the `fitText.firstDraft` phase, an initial draft is generated
and its length is evaluated.
If necessary, the `fitText.rewrite` phase and then the
`fitText.finish` phase are executed.
The final generated text is saved to the `result` directory,
and the `.json` file that specifies the generation conditions
is moved to the `archive` directory.
If an error occurs during processing,
the `.json` file is moved to the `error` directory.

## Directory layout
The following shows the directory and file structure included in this repository:

```
fitText/
+- gateToAgenTalk.py      # Watches the gate directory and starts AgenTalk sessions
+- phases/                # Processing phases of fitText
|   +- firstDraft.py      # Generates the initial draft
|   +- rewrite.py         # Rewrites the text to adjust length
|   +- finish.py          # Finalizes the generated text
|   +- error.py           # Error handling phase
|   +- util.py            # Shared utilities
+- prompts/               # Prompt templates used by each phase
|   +- firstDraft.txt
|   +- rewriteLess.txt
|   +- rewriteMore.txt
+- sampleParam.json       # Example input JSON file
+- requirements.txt
+- README.md
+- README_jp.md
```

The following directories are **created automatically at runtime**
when `gateToAgenTalk.py` is executed and are therefore **not included in the repository**:

- `gate/`    – Drop `.json` files here to trigger processing
- `result/`  – Generated text files
- `archive/` – Successfully processed `.json` files
- `error/`   – `.json` files that caused errors

## Input JSON format
fitText is triggered by dropping a `.json` file into the `gate/` directory.  
The JSON specifies generation constraints
(target length and required keywords) and optional writing hints.

### Schema
- `schema` (string, required)  
  Must be `"fitText"`.

- `version` (number, required)  
  Schema version. Currently `1`.

- `target` (object, required)  
  - `target.chars` (number, required)  
    Target character count for the generated text.  
  - `target.tolerance_ratio` (number, required)  
    Allowed relative deviation from `target.chars` (e.g., `0.10` means within plus or minus 10%).

- `keywords` (object, required)  
  - `keywords.required` (array of strings, required)  
    All strings in this list must appear in the generated text **as-is** (no spelling changes).

- `prompt` (object, optional)  
  Optional hints to guide the content and style.  
  - `prompt.topic` (string, optional)  
    A short topic or theme for the text.  
  - `prompt.notes` (string, optional)  
    Additional constraints or style notes (e.g., "avoid bullet points").

### Example
```json
{
  "schema": "fitText",
  "version": 1,
  "target": {
    "chars": 600,
    "tolerance_ratio": 0.10
  },
  "keywords": {
    "required": [
        "AI agents",
        "the need for parallel and distributed processing"
    ]
  },
  "prompt": {
    "topic": "The future society shaped by AI",
    "notes": "Minimize technical...(See below for full text)"
  }
}
```

Full text of "notes": "Minimize technical jargon and write for a general engineering audience. Do not use bullet points."

### Notes
The acceptable character count range is calculated as:
chars * (1-tolerance_ratio) to chars * (1+tolerance_ratio).

To avoid reading a partially written file,
it is recommended to place the JSON file into gate/ using mv.

## Quick start
AgenTalk is designed as a parallel execution platform,
and running it in a full-scale configuration can easily become complex.
In this section,
we focus on simplicity and demonstrate how to run fitText on a single node,
without considering scale-out or distributed deployment.

### Preparing the execution environment
Open three terminals and log in to the same Linux host from each of them.

We will refer to these terminals as the *reactor terminal*,
the *watcher terminal*, and the *working terminal*.
Since all terminals operate on the same Linux host,
AgenTalk runs here as a single compute node.

#### Working in the reactor terminal
In this terminal, start the AgenTalk reactor.
The detailed procedure is described in the README at the root of this repository.
In short, after starting the Redis server,
move to the repository root and run `agt start` to launch the reactor.
If the AgenTalk reactor is already running, this step can be skipped.

#### Working in the working terminal
##### Registering a remote node
Following the instructions in the repository-level README, register a remote node.
In this quick-start setup, the remote node runs on the same Linux host as the reactor.

##### Checking tickets
AgenTalk phase execution is controlled by a ticket-based load management mechanism.
Before proceeding, confirm that processing tickets are available.

Use `agt at` to add a ticket (*addTicket*),
and `agt ct` to check the number of tickets (*countTicket*).
Having at least one ticket is sufficient for this example.

##### Registering the fitText phases
Move to the `phases` directory and run `agt reg .`.
If the registration succeeds,
the following messages will appear in the reactor terminal:

```
Phase 'fitText.rewrite' is loaded.
Phase 'fitText.error' is loaded.
Phase 'fitText.firstDraft' is loaded.
Phase 'fitText.finish' is loaded.
```

After this, switch from the working terminal to the watcher terminal.

#### Working in the watcher terminal
Make sure the current directory is the top-level directory of this repository.
Then run `python gateToAgenTalk.py` to start the script that watches the `gate` directory.
If the script starts successfully,
the message `started gateToAgenTalk.py` will be displayed.

### Starting text generation
Return to the working terminal and move to the repository root.
Copy `sampleParam.json` into the `gate` directory:
`cp sampleParam.json gate/`.

The running `gateToAgenTalk.py` script detects the addition of
`sampleParam.json` and outputs:

```
[0] detect new file: ./gate/sampleParam.json
```

This triggers the `fitText.firstDraft` phase via `gateToAgenTalk.py`.
On the reactor terminal, the AgenTalk reactor prints:

```
=== START GENERATION: sampleParam.json
```

After a short while,
the generated text is displayed, followed by:

```
FINISH gate/sampleParam.json
```

This indicates that text generation by `sampleParam.json` has completed.
The generated output is written to the `result` directory.

The `sampleParam.json` file placed in the `gate` directory is
renamed with a timestamp and moved to the `archive` directory after processing.

If an error occurs during text generation,
the file is moved to the `error` directory instead of `archive`.

If text generation does not start,
check whether `sampleParam.json` already exists in the `gate` directory.
Since `gateToAgenTalk.py` only detects newly added files,
the `fitText.firstDraft` phase will not be triggered
if a file with the same name is already present.

## Troubleshooting
### Ollama is not installed or not running
fitText relies on a local LLM provided via Ollama.
If Ollama is not installed or the Ollama service is not running,
text generation will not start.

Make sure that Ollama is installed and accessible from the command line.
For installation instructions, see the official Ollama documentation.

You can verify that Ollama is available by running:

```
ollama list
```

If this command fails,
install or start Ollama before running fitText.


<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Security Policy</h1>
</div>

## Supported Versions

Only the latest tagged release gets security fixes.

## Reporting a Vulnerability

Open a GitHub issue with label `security`. Describe the vulnerability type and affected component.
Do not include exploit code in public issues.

I aim to respond within 72 hours and provide a fix within 14 days for confirmed vulnerabilities.

## Security Design Notes

AdapterForge runs entirely on your machine and only shells out to tools you already have installed (`mlx_lm`, `ollama`, a local llama.cpp checkout). It makes no network calls of its own and does not read, write, or transmit anything outside the paths you pass on the command line.

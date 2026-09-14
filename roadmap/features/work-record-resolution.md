---
id: work-record-resolution
title: 'Deterministic Work Record pickup and handoff'
status: active
priority: high
commitment: committed
---

# Deterministic Work Record pickup and handoff

## Summary

Expose a read-only packaged resolver for the canonical local Work Record. A persisted `agent-workflow:<slug>` identity wins over branch inference and returns a bounded structured result containing its repository-relative path and parsed state.

## Why

Agents and adjacent tools can otherwise select a different record after a branch change, scan by recency, or confuse workflow readiness with delivery state. Pickup and handoff need one portable identity without adding a service or task registry.

## In scope

- Trusted-install checker command with stable found, absent, and error results.
- Supplied-reference precedence and documented first-prefix branch fallback.
- Repository-relative configured paths contained within the selected checkout for reads and writes.
- Agent guidance that preserves source and Work Record identity through pickup and handoff.
- Source and packaged CLI tests proving lookup is read-only.

## Out of scope

Automatic Pallium or hook consumption, repository-provided executable trust, Jira, readiness/Redline/applicability decisions, merge/release state, record creation, and record scans.

A future automatic consumer may proceed only after trusted setup provides a provider-owned absolute resolver path and a startup schema handshake. Missing or stale setup must degrade without executing repository code.

## Done When

The source and packaged resolver contract passes on Windows/POSIX-compatible paths, unsafe paths cannot escape on read or write, guidance and distribution are synchronized, and the required reviews and CI pass.
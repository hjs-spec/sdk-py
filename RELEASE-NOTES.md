# Software 0.7.1

- Supply the full MIT license already declared in README and package metadata.
- Publish SPDX license metadata and include LICENSE and NOTICE.md in both wheel and source distributions.
- Verify package versions, license metadata and distributed license bytes before publishing.

Runtime behavior and JEP Core 0.7 semantics are unchanged. Existing published artifacts are not overwritten.

# JEP Core 0.7 migration

- Default API path is now `/v0.7/events/*`.
- Events use stable `id` and no longer require Core `nonce`.
- Validation results use `status`, independent `checks`, `event_identity`, and optional `acceptance`.
- D/T/V Core minimum shapes are validated before requests are sent.
- Historical pre-0.7 verification remains explicit; there is no automatic fallback.


The earlier 0.6 release added `conformance_class` passthrough. Current releases retain it while using the Core 0.7 profile; the wire major remains `jep: "1"`.

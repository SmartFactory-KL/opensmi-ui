# EntityId and why they are used

Although OPCUA nodes usually have a (namespace) unique nodeId, I choose to not use that for primary identification.
Reasons being:

- UUIDs are always the same length - nodeIds can be quite long
- nodeIds could contain non-url-safe symbols (mainly : and = ) - would need encoding which makes it annoying to use
- entityIds are globally unique and not namespace-unique (mostly thinking about the multi-server scenario)
- entityIds are generated on demand, so every connect creates new ones. This helps in avoiding re-use of components which might lead to undefined behaviour.

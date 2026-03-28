# Skills

## Goal

Skills are reusable capability packages that can be attached to one or more agents.

They should scale to future areas such as:

- procurement analysis
- supplier risk
- pricing intelligence
- site retrieval
- document QA
- report formatting
- monitoring and alerting

## Skill package contract

Each skill folder should contain:

- `skill.json`
- `SYSTEM.md`

Optional files:

- `INPUTS.md`
- `OUTPUTS.md`
- `EXAMPLES.md`

## Metadata fields

Recommended `skill.json` fields:

- `name`
- `version`
- `description`
- `tags`
- `compatible_agents`
- `allowed_tools`
- `priority`
- `enabled`

## Runtime composition

At runtime, the application should:

1. discover enabled skills
2. select relevant skills for the current workflow or agent
3. merge markdown sections in a deterministic order
4. build the final system prompt payload

This approach keeps skill logic scalable without hardcoding every future skill into the app.

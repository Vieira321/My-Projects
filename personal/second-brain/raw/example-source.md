# The Twelve-Factor App (raw note)

Source: https://12factor.net (public methodology)

Quick notes I took while reading the Twelve-Factor App methodology — a set of
principles for building software-as-a-service apps that are portable and
scalable. Key ones I want to remember:

- Codebase: one codebase tracked in version control, many deploys.
- Config: store config in the environment, never in code.
- Backing services: treat databases, queues, caches as attached resources.
- Build, release, run: keep these three stages strictly separated.
- Processes: execute the app as stateless processes.
- Logs: treat logs as event streams, don't manage log files inside the app.

Originally formulated by engineers at Heroku.

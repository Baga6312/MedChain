# Local logging

The local stack stores backend application logs without sending them to a third party:

```text
Backend JSON logs
        ↓
Local ./logs directory
        ↓
Fluent Bit
        ↓
Elasticsearch
        ↓
Kibana
```

Start it with:

```powershell
docker compose up -d
```

Open Kibana at `http://localhost:5601` and create a data view named
`medchain-logs`. Select `timestamp` as the time field.

Elasticsearch data is persisted in the `elasticsearchdata` Docker volume.
The raw backend log file is kept in `./logs` and ignored by Git.

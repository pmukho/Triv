# Running Tests with Docker

This module includes a Dockerfile for running tests

### Steps

1. **Build the Docker Image**

   From the project root, run:

   ```bash
    docker build -f gamemaster/tests/Dockerfile -t gamemaster-tests .
   ```

2. **Run the Tests**

   Run the container:

   ```bash
   docker run --rm gamemaster-tests
   ```

This Dockerfile sets `PYTHONPATH=/app/gamemaster` so your test files can use:

```python
from main import ConnectionManager
from gamemaster import GameMaster
from gmfactory import GmFactory
```
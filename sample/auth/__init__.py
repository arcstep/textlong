"""
例子：

```
from fastapi import FastAPI
from illufly.fastapi import create_auth_api

app = FastAPI()
app.include_router(create_auth_api())
```
"""

from .auth import create_auth_api, get_current_user

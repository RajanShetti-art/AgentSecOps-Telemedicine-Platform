from __future__ import annotations
import jwt
import time

# IMPORTANT: this uses the secret currently configured in the repo for testing only
secret = "3Wm8sL9qVfZtY5rN_hc8KpQ2b7xR0aEjU6dO4cB1sGzFvTnY"
payload = {"sub": "test@example.com", "iat": int(time.time())}
print(jwt.encode(payload, secret, algorithm="HS256"))

# Session architecture

The authentication service owns session issuance and rotation. Rotation must be atomic from the caller's perspective.

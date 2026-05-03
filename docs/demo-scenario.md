# Demo Scenario

1. Start the stack with `docker compose up --build`.
2. Open `http://localhost:5173`.
3. Login as `admin@example.com`.
4. Create a user named `user@example.com`.
5. Assign the `KEY_USER` role to the user.
6. Create a key named `customer-data-key`.
7. Login as `user@example.com`.
8. Encrypt a message.
9. Decrypt the message.
10. Login as admin or auditor.
11. View audit logs.
12. Rotate the key.
13. Encrypt a new message.
14. Show that the old ciphertext still decrypts with the previous key version.

This demonstrates authentication, authorization, KMS operations, key rotation, and auditability.


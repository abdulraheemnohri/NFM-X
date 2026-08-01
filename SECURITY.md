# NFM-X Security Documentation

## Overview
Comprehensive security model for AI memories and data.

## Authentication
Uses API keys for authentication.
Authorization: Bearer YOUR_API_KEY

## Authorization
### Permission Levels
READ, WRITE, EVOLVE, CONFIRM, EXPORT, ADMIN

### Memory Scopes
PRIVATE, AGENT, PROJECT, TEAM, SHARED, SYSTEM

## Sensitive Memory Policy
### Classification
PUBLIC, INTERNAL, CONFIDENTIAL, SECRET

### Policy Options
store, do_not_store, ask_before_store, temporary_only, encrypted, restricted

## Encryption
- At-Rest: SQLite (SQLCipher), Vector Index, Documents, Backups
- Configuration: ENCRYPTION_ENABLED, ENCRYPTION_KEY, ENCRYPTION_ALGORITHM

## Integrity Verification
- Hash Chaining: M001 hash -> M002 + M001 hash -> M003 + M002 hash
- Checkpoints: Periodic integrity verification
- Digital Signatures: Optional signing

## Audit Logging
Logs all actions with timestamp, action, user, memory_id, IP, user_agent, status.

## Network Security
- TLS/SSL: Enable HTTPS
- CORS: Configure origins
- Rate Limiting: 100 requests/min, 10/sec burst

## Data Privacy
### Local-Only Mode
- No cloud storage
- No telemetry
- No external services
- Everything local

### GDPR Compliance
- Right to Access
- Right to Erasure
- Data Portability
- Consent Management

## Secure Deployment
- Enable HTTPS
- Use strong API keys
- Enable encryption
- Configure permissions
- Set up audit logging
- Enable rate limiting
- Regular backups
- Monitor activity

## Best Practices
### For Users
1. Use strong API keys
2. Limit permissions
3. Rotate keys regularly
4. Monitor activity
5. Backup data
6. Keep updated

### For Developers
1. Input validation
2. Sanitize outputs
3. Parameterized queries
4. Limit data exposure
5. Handle errors securely
6. Use HTTPS

## Known Limitations
- No MFA
- No IP Whitelisting
- No Time-Based Restrictions
- No Geographic Restrictions

## Contacts
- GitHub: https://github.com/abdulraheemnohri/NFM-X/security
- Maintainer: Abdulraheem Nohari (@abdulraheemnohri)
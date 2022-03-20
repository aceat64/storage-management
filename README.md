# storage-management

## Process

### User creates ticket

* Only if user_id.banned_until = null or user_id.banned_unit < t.now (not banned or ban elapsed)
* Only if user_id has no tickets with finished_at = null (active tickets)
* Only if spot_id has no tickets with finished_at null (no active tickets)
* created_at set to t.now
* expires_at set to t+7d

### User closes ticket

* Only if finished_at = null (ticket is still active)
* If t.now <= expires_at, user_id.banned_until set to 7d - (t.now - created_at)
* If t.now > expires_at, user_id.banned_until set to t+14d

### Scheduled checks

Run every 5 minutes, iterate over each ticket with finished_at = null (active tickets)

* If t+48h > expires_at and there is no notification of type "48hour", send a "48 hour" notification
* If t+24h > expires_at and there is no notification of type "24hour", send a "24 hour" notification
* If t.now > expires_at and there is no notificaiton of type "expired", send an "expired" notification
* If t+48h > expires_at+7d and there is no notification of type "48hour_expired", send a "48 hour forfiture" notification
* If t+24h > expires_at+7d and there is no notification of type "24hour_expired", send a "24 hour forfiture" notification
* If t.now > expires_at+7d and there is no notificaiton of type "forfiture", send a "forfiture" notification

# Twitter/X API Endpoints

Base path: `/v1/twitter`

## Profile

### Get Profile
```
GET /v1/twitter/profile?handle={username}
```
Public profile data including stats (followers, following, tweet count) and metadata.

## Communities

### Community Info
```
GET /v1/twitter/community?community_id={id}
```
Details about a Twitter/X community.

### Community Tweets
```
GET /v1/twitter/community/tweets?community_id={id}&cursor={cursor}
```
Paginated tweets from a specific Twitter/X community.

## Notes

- Twitter/X endpoints scrape public data only — no private accounts or DMs
- Use `trim=true` to reduce response size
- Use `cursor` for pagination on community tweets

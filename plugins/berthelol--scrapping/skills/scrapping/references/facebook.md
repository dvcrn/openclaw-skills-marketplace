# Facebook API Endpoints

Base path: `/v1/facebook`

## Profile & Pages

### Profile
```
GET /v1/facebook/profile?handle={page_name}
```
Public page data. Pass `get_business_hours=true` to include business hours.

## Content

### Posts
```
GET /v1/facebook/posts?handle={page_name}&cursor={cursor}
```
Unified endpoint for posts and reels from a Facebook page (previously separate endpoints).

### Reels
```
GET /v1/facebook/reels?handle={page_name}&cursor={cursor}
```
Facebook page reels, 10 per request. Requires manual pagination using `next_page_id` and `cursor`.

### Group Posts
```
GET /v1/facebook/group/posts?group_id={id}&cursor={cursor}
```
Public posts from a Facebook group.

### Transcript
```
GET /v1/facebook/transcript?url={post_url}
```
Dedicated transcript endpoint for Facebook posts/reels. Pass the post URL.

## Comments

### Post Comments
```
GET /v1/facebook/post/comments?url={post_url}&cursor={cursor}
```
Comments on a Facebook post. Passing `feedback_id` instead of URL is significantly faster because it skips the URL resolution step — use it when you've already fetched the post and have the `feedback_id` from the response.

```
GET /v1/facebook/post/comments?feedback_id={id}&cursor={cursor}
```

## Ad Library

### Search Ads
```
GET /v1/facebook/adLibrary/search/ads?query={company_name}&cursor={cursor}
```
Search the Meta Ad Library. Note the camelCase `adLibrary` in the path — this is different from most other endpoints and a common source of 404 errors.

Parameters:
- `sort_by` — sort by `total_impressions` or `relevancy_monthly_grouped`
- `start_date` / `end_date` — filter by date range
- `language` — filter by language

### Ad Details
```
GET /v1/facebook/ad?url={ad_url}
```
Full details for a specific ad. Also accepts a URL parameter directly. Includes EU transparency data.

## Notes

- Posts endpoint is unified (posts + reels together)
- Facebook reels endpoint returns 10 per request, uses manual pagination with `next_page_id` and `cursor`
- For comments, using `feedback_id` is much faster than passing the URL
- Ad library supports sorting by `total_impressions` or `relevancy_monthly_grouped`, plus date and language filters
- AI transcripts limited to videos under 2 minutes
- Use `trim=true` to reduce response size

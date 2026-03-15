# TikTok API Endpoints

Base path: `/v1/tiktok`

## Profile & User Data

### Get Profile
```
GET /v1/tiktok/profile?handle={username}
```
Returns public profile data: bio, follower/following counts, total likes, avatar, verified status. Response fields include `statsV2.followerCount`, `statsV2.followingCount`, `statsV2.heartCount` for metrics.

### Audience Demographics
```
GET /v1/tiktok/user/demographics?handle={username}
```
Returns audience country breakdown. **Costs 26 credits** because it requires heavy computation on the backend — only use when the user specifically needs audience geography data, not for general profile lookups.

### Followers
```
GET /v1/tiktok/user/followers?handle={username}&cursor={cursor}
```
Paginated list of followers.

### Following
```
GET /v1/tiktok/user/following?handle={username}&cursor={cursor}
```
Paginated list of accounts the user follows.

## Video Content

### User Posts (Profile Videos)
```
GET /v1/tiktok/profile/videos?handle={username}&cursor={cursor}&sort_by={sort}
```
Paginated list of a user's videos. `sort_by=popular` returns most popular first.
Response contains `aweme_list` array with video objects. Each video has `statistics` with `play_count`, `digg_count` (likes), `comment_count`, `share_count`, `collect_count`.

### Video Info
```
GET /v1/tiktok/video?video_id={id}
```
Full details for a single video: description, play/like/comment/share counts, music info, hashtags. Use this when you already have a specific `video_id` and need detailed metadata — it's cheaper than fetching all profile videos when you only need one.

### Video Transcript
```
GET /v1/tiktok/video/transcript?video_id={id}
```
Returns the transcript of a TikTok video. Note: AI-generated transcripts are limited to videos under 2 minutes.

### Video Comments
```
GET /v1/tiktok/video/comments?video_id={id}&cursor={cursor}
```
Paginated comments on a video.

### Live Stream
```
GET /v1/tiktok/user/live?handle={username}
```
Data from a user's current or recent live stream.

## Search

### Search by Keyword
```
GET /v1/tiktok/search/keyword?query={keyword}&cursor={cursor}
```
Search TikTok videos matching a keyword. Use this when a user wants to find content about a topic — it returns videos ranked by relevance, which is more useful than browsing hashtags when the user doesn't know the exact tag creators use.

### Top Search
```
GET /v1/tiktok/search/top?query={keyword}
```
Returns the "Top" search results including photo carousels and videos. Use this instead of keyword search when you need mixed content types (not just videos) — photo carousels won't appear in regular keyword search results.

### Search by Hashtag
```
GET /v1/tiktok/search/hashtag?query={hashtag}&cursor={cursor}
```
Videos tagged with a specific hashtag.

### Search Users
```
GET /v1/tiktok/search/users?query={keyword}&cursor={cursor}
```
Search for TikTok users.

## Trending & Discovery

### Popular Videos
```
GET /v1/tiktok/videos/popular?period={period}&region={region}
```
Filter trending videos by time period and region. Good for research and analytics — returns curated popular content with engagement data.

### Popular Creators
```
GET /v1/tiktok/creators/popular?min_followers={count}&audience_country={country}
```
Discover creators by follower count, audience country, and engagement.

### Popular Hashtags
```
GET /v1/tiktok/hashtags/popular?period={period}
```
Trending hashtags with time-period filtering.

### Popular Songs
```
GET /v1/tiktok/songs/popular
```
Trending music on TikTok (30-second previews max).

### Trending Feed
```
GET /v1/tiktok/get-trending-feed?region={region}
```
The raw trending feed from TikTok for a specific region. Returns the same content users see on the "For You" trending tab. Use `region=US`, `region=UK`, etc.

## Music

### Song Details
```
GET /v1/tiktok/song?song_id={id}
```
Metadata for a specific song.

### TikToks Using Song
```
GET /v1/tiktok/song/videos?song_id={id}&cursor={cursor}
```
Videos that use a specific song.

## TikTok Shop

### Shop Search
```
GET /v1/tiktok/shop/search?query={keyword}
```
Search TikTok Shop products.

### Product Details
```
GET /v1/tiktok/product?product_id={id}
```
Full product details including exact stock count, related promotional videos.

### Product Reviews
```
GET /v1/tiktok/product/reviews?product_id={id}
```
Returns up to 100 product reviews at once.

## Common parameters

- `trim=true` — trimmed response with key fields only
- `cursor` — pagination cursor from previous response
- `sort_by=popular` — sort user posts by popularity

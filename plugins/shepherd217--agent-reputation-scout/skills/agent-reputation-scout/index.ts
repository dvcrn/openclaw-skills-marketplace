import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

interface AgentProfile {
  name: string;
  karma: number;
  followerCount: number;
  followingCount: number;
  description: string;
  isClaimed: boolean;
  recentPosts: number;
  avgEngagement: number;
}

interface Post {
  id: string;
  title?: string;
  content: string;
  author: string;
  upvotes: number;
  replyCount: number;
  createdAt: Date;
  platform: 'moltbook' | 'clawk';
}

interface ScoutResult {
  agent: AgentProfile;
  reputationScore: number;
  engagementQuality: number;
  topicMatch: number;
  recommendation: 'high' | 'medium' | 'low';
  reason: string;
}

export class AgentReputationScout {
  private moltbookKey: string;
  private clawkKey: string;
  private userInterests: string[];

  constructor(interests: string[] = []) {
    this.moltbookKey = process.env.MOLTBOOK_API_KEY || '';
    this.clawkKey = process.env.CLAWK_API_KEY || '';
    this.userInterests = interests;
  }

  /**
   * Calculate reputation score for an agent
   */
  calculateReputationScore(agent: AgentProfile): number {
    const karmaWeight = 0.3;
    const followerWeight = 0.2;
    const engagementWeight = 0.3;
    const verificationWeight = 0.2;

    // Normalize karma (cap at 50k for scaling)
    const karmaScore = Math.min(agent.karma, 50000) / 50000;

    // Follower ratio (following back is good, but not too many)
    const followRatio = agent.followerCount / (agent.followingCount + 1);
    const followerScore = Math.min(followRatio, 5) / 5; // Cap at 5:1 ratio

    // Engagement quality
    const engagementScore = Math.min(agent.avgEngagement / 10, 1); // 10+ avg engagement = max

    // Verification bonus
    const verificationScore = agent.isClaimed ? 1 : 0.3;

    return (
      karmaScore * karmaWeight +
      followerScore * followerWeight +
      engagementScore * engagementWeight +
      verificationScore * verificationWeight
    ) * 100;
  }

  /**
   * Score a post's reply opportunity
   */
  scoreReplyOpportunity(post: Post, authorProfile: AgentProfile): {
    score: number;
    recommendation: string;
  } {
    const authorRep = this.calculateReputationScore(authorProfile);
    
    // Freshness score (posts < 2 hours old score higher)
    const hoursOld = (Date.now() - post.createdAt.getTime()) / (1000 * 60 * 60);
    const freshnessScore = Math.max(0, 1 - hoursOld / 24);

    // Reply saturation (fewer replies = less competition)
    const saturationScore = Math.max(0, 1 - post.replyCount / 10);

    // Topic match
    const topicMatch = this.calculateTopicMatch(post.content);

    const totalScore = (
      authorRep * 0.4 +
      freshnessScore * 30 +
      saturationScore * 20 +
      topicMatch * 10
    );

    let recommendation = 'low';
    if (totalScore > 70) recommendation = 'high';
    else if (totalScore > 40) recommendation = 'medium';

    return {
      score: Math.round(totalScore),
      recommendation: `${recommendation.toUpperCase()} - ${this.getRecommendationReason(totalScore, authorProfile, post)}`
    };
  }

  /**
   * Calculate how well post matches user interests
   */
  private calculateTopicMatch(content: string): number {
    if (this.userInterests.length === 0) return 0.5;

    const lowerContent = content.toLowerCase();
    let matches = 0;

    for (const interest of this.userInterests) {
      if (lowerContent.includes(interest.toLowerCase())) {
        matches++;
      }
    }

    return matches / this.userInterests.length;
  }

  /**
   * Get human-readable recommendation reason
   */
  private getRecommendationReason(score: number, author: AgentProfile, post: Post): string {
    const reasons: string[] = [];

    if (author.karma > 5000) reasons.push(`High karma author (${author.karma})`);
    if (post.replyCount < 3) reasons.push(`Low competition (${post.replyCount} replies)`);
    if (post.upvotes > 50) reasons.push(`Trending (${post.upvotes} upvotes)`);
    if (author.isClaimed) reasons.push('Verified agent');

    return reasons.join(', ') || 'Average opportunity';
  }

  /**
   * Fetch Moltbook agent profile
   */
  async fetchMoltbookProfile(name: string): Promise<AgentProfile | null> {
    try {
      const response = await axios.get(
        `https://www.moltbook.com/api/v1/agents/profile?name=${name}`,
        { headers: { Authorization: `Bearer ${this.moltbookKey}` } }
      );

      const agent = response.data.agent;
      return {
        name: agent.name,
        karma: agent.karma,
        followerCount: agent.follower_count,
        followingCount: agent.following_count,
        description: agent.description,
        isClaimed: agent.is_claimed,
        recentPosts: agent.posts_count || 0,
        avgEngagement: this.calculateAvgEngagement(agent)
      };
    } catch (error) {
      console.error(`Failed to fetch Moltbook profile for ${name}:`, error);
      return null;
    }
  }

  /**
   * Fetch Clawk agent profile
   */
  async fetchClawkProfile(name: string): Promise<AgentProfile | null> {
    try {
      const response = await axios.get(
        `https://clawk.ai/api/v1/agents/${name}`,
        { headers: { Authorization: `Bearer ${this.clawkKey}` } }
      );

      const agent = response.data;
      return {
        name: agent.name,
        karma: agent.followerCount * 10, // Clawk doesn't have karma, estimate
        followerCount: agent.followerCount,
        followingCount: agent.followingCount || 0,
        description: agent.description || '',
        isClaimed: true, // Clawk requires claim
        recentPosts: 0,
        avgEngagement: agent.avgEngagement || 0
      };
    } catch (error) {
      console.error(`Failed to fetch Clawk profile for ${name}:`, error);
      return null;
    }
  }

  /**
   * Calculate average engagement from agent data
   */
  private calculateAvgEngagement(agent: any): number {
    if (!agent.posts_count || agent.posts_count === 0) return 0;
    // Estimate based on karma and posts
    return (agent.karma || 0) / (agent.posts_count * 10);
  }

  /**
   * Fetch Clawk post by ID
   */
  async fetchClawkPost(clawkId: string): Promise<Post | null> {
    try {
      // Clawk doesn't have a direct post endpoint, fetch from timeline and filter
      const response = await axios.get(
        `https://clawk.ai/api/v1/timeline`,
        { headers: { Authorization: `Bearer ${this.clawkKey}` } }
      );

      const posts = response.data.posts || response.data || [];
      const post = posts.find((p: any) => p.id === clawkId || p._id === clawkId);
      
      if (!post) return null;

      return {
        id: post.id || post._id,
        content: post.content || post.text || '',
        author: post.author?.name || post.author || '',
        upvotes: post.upvotes || post.likes || post.engagement?.upvotes || 0,
        replyCount: post.replyCount || post.replies || post.commentCount || 0,
        createdAt: new Date(post.createdAt || post.timestamp || Date.now()),
        platform: 'clawk'
      };
    } catch (error) {
      console.error(`Failed to fetch Clawk post ${clawkId}:`, error);
      return null;
    }
  }

  /**
   * Score a Clawk post's reply opportunity
   */
  async scoreClawkPost(clawkId: string): Promise<{
    score: number;
    recommendation: string;
    post?: Post;
    authorProfile?: AgentProfile;
  } | null> {
    const post = await this.fetchClawkPost(clawkId);
    if (!post) return null;

    const authorProfile = await this.fetchClawkProfile(post.author);
    if (!authorProfile) {
      // Still score with limited info
      const fallbackResult = this.scoreReplyOpportunity(post, {
        name: post.author,
        karma: 0,
        followerCount: 0,
        followingCount: 0,
        description: '',
        isClaimed: false,
        recentPosts: 0,
        avgEngagement: 0
      });
      return {
        score: fallbackResult.score,
        recommendation: fallbackResult.recommendation,
        post
      };
    }

    const result = this.scoreReplyOpportunity(post, authorProfile);
    return {
      score: result.score,
      recommendation: result.recommendation,
      post,
      authorProfile
    };
  }

  /**
   * Get Clawk recommendations from explore feed
   */
  async getClawkRecommendations(limit: number = 10): Promise<{
    posts: Array<Post & { authorProfile?: AgentProfile; opportunityScore: number }>;
    topAgents: AgentProfile[];
  }> {
    try {
      const response = await axios.get(
        `https://clawk.ai/api/v1/explore?sort=ranked`,
        { headers: { Authorization: `Bearer ${this.clawkKey}` } }
      );

      const posts = response.data.posts || response.data || [];
      const processedPosts: Array<Post & { authorProfile?: AgentProfile; opportunityScore: number }> = [];
      const authorCache = new Map<string, AgentProfile>();

      for (const post of posts.slice(0, limit)) {
        const normalizedPost: Post = {
          id: post.id || post._id,
          content: post.content || post.text || '',
          author: post.author?.name || post.author || '',
          upvotes: post.upvotes || post.likes || post.engagement?.upvotes || 0,
          replyCount: post.replyCount || post.replies || post.commentCount || 0,
          createdAt: new Date(post.createdAt || post.timestamp || Date.now()),
          platform: 'clawk'
        };

        // Fetch author profile (with caching)
        let authorProfile = authorCache.get(normalizedPost.author);
        if (!authorProfile) {
          authorProfile = await this.fetchClawkProfile(normalizedPost.author);
          if (authorProfile) {
            authorCache.set(normalizedPost.author, authorProfile);
          }
        }

        const scoreResult = this.scoreReplyOpportunity(
          normalizedPost,
          authorProfile || {
            name: normalizedPost.author,
            karma: 0,
            followerCount: 0,
            followingCount: 0,
            description: '',
            isClaimed: false,
            recentPosts: 0,
            avgEngagement: 0
          }
        );

        processedPosts.push({
          ...normalizedPost,
          authorProfile: authorProfile || undefined,
          opportunityScore: scoreResult.score
        });
      }

      // Sort by opportunity score
      processedPosts.sort((a, b) => b.opportunityScore - a.opportunityScore);

      // Extract unique top agents
      const topAgents = Array.from(authorCache.values())
        .sort((a, b) => this.calculateReputationScore(b) - this.calculateReputationScore(a))
        .slice(0, 5);

      return { posts: processedPosts, topAgents };
    } catch (error) {
      console.error('Failed to fetch Clawk recommendations:', error);
      return { posts: [], topAgents: [] };
    }
  }

  /**
   * Fetch posts from both platforms and merge recommendations
   */
  async getUnifiedRecommendations(limit: number = 10): Promise<{
    posts: Array<Post & { authorProfile?: AgentProfile; opportunityScore: number }>;
    topAgents: AgentProfile[];
  }> {
    const [clawkResults] = await Promise.all([
      this.getClawkRecommendations(limit),
      // Moltbook recommendations would go here when implemented
    ]);

    // Merge and sort by opportunity score
    const allPosts = [...clawkResults.posts];
    allPosts.sort((a, b) => b.opportunityScore - a.opportunityScore);

    return {
      posts: allPosts.slice(0, limit),
      topAgents: clawkResults.topAgents
    };
  }

  /**
   * Search for high-value agents by topic
   */
  async searchAgents(platform: 'moltbook' | 'clawk', topic: string, minKarma: number = 100): Promise<ScoutResult[]> {
    // This would integrate with platform search APIs
    // For now, return mock data structure
    console.log(`Searching ${platform} for agents discussing "${topic}" with min karma ${minKarma}`);
    return [];
  }

  /**
   * Get daily digest of opportunities
   */
  async generateDailyDigest(): Promise<string> {
    const report: string[] = [
      '📊 Agent Reputation Scout - Daily Digest',
      '',
      `Your Interests: ${this.userInterests.join(', ')}`,
      '',
      '🔥 High-Value Opportunities:',
    ];

    // Would fetch real data here
    report.push('- No new opportunities found (implementing fetch logic)');

    report.push('', '💡 Tip: Reply to posts within 2 hours for maximum visibility.');

    return report.join('\n');
  }
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const scout = new AgentReputationScout(['domains', 'arbitrage', 'deals']);

  switch (command) {
    case 'digest':
      scout.generateDailyDigest().then(console.log);
      break;
    case 'profile':
      if (args[1]) {
        const platform = args[2] as 'moltbook' | 'clawk' || 'moltbook';
        const fetchFn = platform === 'clawk' 
          ? scout.fetchClawkProfile.bind(scout)
          : scout.fetchMoltbookProfile.bind(scout);
        
        fetchFn(args[1]).then(profile => {
          if (profile) {
            const score = scout.calculateReputationScore(profile);
            console.log(`@${profile.name} (${platform})`);
            console.log(`Karma: ${profile.karma}`);
            console.log(`Reputation Score: ${score.toFixed(1)}/100`);
            console.log(`Followers: ${profile.followerCount}`);
          } else {
            console.log(`Profile not found: ${args[1]} on ${platform}`);
          }
        });
      }
      break;
    case 'score-clawk':
      if (args[1]) {
        scout.scoreClawkPost(args[1]).then(result => {
          if (result) {
            console.log(`Post: ${result.post?.content.substring(0, 80)}...`);
            console.log(`Author: @${result.post?.author}`);
            console.log(`Opportunity Score: ${result.score}/100`);
            console.log(`Recommendation: ${result.recommendation}`);
          } else {
            console.log('Post not found or error occurred');
          }
        });
      }
      break;
    case 'recommend-clawk':
      scout.getClawkRecommendations(parseInt(args[1]) || 10).then(result => {
        console.log('🔥 Top Clawk Opportunities:');
        console.log('');
        result.posts.forEach((post, i) => {
          console.log(`${i + 1}. @${post.author} (${post.opportunityScore}/100)`);
          console.log(`   ${post.content.substring(0, 100)}...`);
          console.log(`   ${post.replyCount} replies | ${post.upvotes} upvotes`);
          console.log('');
        });
        if (result.topAgents.length > 0) {
          console.log('👑 Top Agents:');
          result.topAgents.forEach(agent => {
            const score = scout.calculateReputationScore(agent);
            console.log(`   @${agent.name} - Score: ${score.toFixed(1)}/100`);
          });
        }
      });
      break;
    case 'recommend-unified':
      scout.getUnifiedRecommendations(parseInt(args[1]) || 10).then(result => {
        console.log('🌐 Unified Recommendations (Moltbook + Clawk):');
        console.log('');
        result.posts.forEach((post, i) => {
          const platform = post.platform === 'clawk' ? '🦞' : '📘';
          console.log(`${i + 1}. ${platform} @${post.author} (${post.opportunityScore}/100)`);
          console.log(`   ${post.content.substring(0, 100)}...`);
          console.log('');
        });
      });
      break;
    default:
      console.log('Usage: agent-scout [digest|profile @name [platform]|score-clawk id|recommend-clawk [limit]|recommend-unified [limit]]');
  }
}

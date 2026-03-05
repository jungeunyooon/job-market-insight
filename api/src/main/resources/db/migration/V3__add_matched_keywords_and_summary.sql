-- Add matched_keywords to posting_skill for deep keyword tracking
ALTER TABLE posting_skill ADD COLUMN IF NOT EXISTS matched_keywords JSONB DEFAULT '[]';

-- Add summary to tech_blog_post (if not exists - it's in entity but might not be in DB)
ALTER TABLE tech_blog_post ADD COLUMN IF NOT EXISTS summary TEXT;

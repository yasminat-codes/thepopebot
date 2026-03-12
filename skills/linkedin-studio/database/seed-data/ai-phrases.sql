-- =============================================================================
-- LinkedIn Studio: AI Phrases Blocklist Seed Data
-- Table: ls_ai_phrases_blocklist
-- Columns: (phrase, category, severity, replacement_suggestions)
-- Total: 346 phrases across 12 categories
-- =============================================================================

BEGIN;

TRUNCATE TABLE ls_ai_phrases_blocklist;

-- =============================================================================
-- Category 1: corporate (48 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('leverage', 'corporate', 'high', ARRAY['use', 'apply', 'employ']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('utilize', 'corporate', 'high', ARRAY['use', 'apply', 'work with']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('synergy', 'corporate', 'high', ARRAY['working together', 'collaboration', 'combined effort']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('synergies', 'corporate', 'high', ARRAY['combined strengths', 'shared advantages', 'joint efforts']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('bandwidth', 'corporate', 'high', ARRAY['time', 'capacity', 'availability']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('ecosystem', 'corporate', 'high', ARRAY['space', 'environment', 'field']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('paradigm shift', 'corporate', 'high', ARRAY['fundamental change', 'major shift', 'big change']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('holistic', 'corporate', 'high', ARRAY['complete', 'full', 'whole']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('scalable', 'corporate', 'high', ARRAY['grows with you', 'expandable', 'flexible']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('robust', 'corporate', 'high', ARRAY['strong', 'solid', 'reliable']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('cutting-edge', 'corporate', 'high', ARRAY['latest', 'newest', 'modern']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('state-of-the-art', 'corporate', 'high', ARRAY['most advanced', 'latest', 'modern']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('best-in-class', 'corporate', 'high', ARRAY['best', 'top', 'leading']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('thought leadership', 'corporate', 'high', ARRAY['original thinking', 'expert perspective', 'informed opinion']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('value proposition', 'corporate', 'high', ARRAY['what makes it worth it', 'why it matters', 'the benefit']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('stakeholder', 'corporate', 'high', ARRAY['decision-maker', 'person involved', 'someone affected']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('actionable', 'corporate', 'high', ARRAY['practical', 'useful', 'doable']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('impactful', 'corporate', 'high', ARRAY['effective', 'meaningful', 'significant']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('deliverable', 'corporate', 'high', ARRAY['finished output', 'result', 'what you hand off']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('deep dive', 'corporate', 'high', ARRAY['close look', 'detailed review', 'thorough look']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('circle back', 'corporate', 'high', ARRAY['follow up', 'revisit', 'come back to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('touch base', 'corporate', 'high', ARRAY['check in', 'connect', 'catch up']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('low-hanging fruit', 'corporate', 'high', ARRAY['easy win', 'quick fix', 'simple improvement']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('move the needle', 'corporate', 'high', ARRAY['make a real difference', 'have an impact', 'change the outcome']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('pain points', 'corporate', 'high', ARRAY['problems', 'frustrations', 'issues']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('gain traction', 'corporate', 'high', ARRAY['build momentum', 'pick up speed', 'start growing']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('take it to the next level', 'corporate', 'high', ARRAY['improve it', 'make it better', 'raise the bar']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('at the end of the day', 'corporate', 'high', ARRAY['ultimately', 'in the end', 'when it counts']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('going forward', 'corporate', 'high', ARRAY['from now on', 'next', 'after this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('pivot', 'corporate', 'high', ARRAY['shift direction', 'change course', 'adjust']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('ideation', 'corporate', 'high', ARRAY['brainstorming', 'generating ideas', 'thinking up ideas']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('knowledge transfer', 'corporate', 'high', ARRAY['teaching', 'sharing what you know', 'training']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('alignment', 'corporate', 'high', ARRAY['agreement', 'shared direction', 'being on the same page']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('cadence', 'corporate', 'high', ARRAY['rhythm', 'schedule', 'pace']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('streamline', 'corporate', 'high', ARRAY['simplify', 'make easier', 'reduce steps']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('best practices', 'corporate', 'high', ARRAY['what actually works', 'proven methods', 'effective approaches']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('key takeaway', 'corporate', 'high', ARRAY['the point', 'what matters', 'the lesson']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('key takeaways', 'corporate', 'high', ARRAY['what matters here', 'the main points', 'what to remember']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('core competency', 'corporate', 'high', ARRAY['strength', 'skill', 'what you do best']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('end-to-end', 'corporate', 'high', ARRAY['from start to finish', 'complete', 'full']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('mission-critical', 'corporate', 'high', ARRAY['essential', 'vital', 'must-have']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('quick wins', 'corporate', 'high', ARRAY['fast results', 'easy improvements', 'immediate gains']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('upskill', 'corporate', 'high', ARRAY['learn', 'develop skills', 'get better at']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('operationalize', 'corporate', 'high', ARRAY['put into practice', 'implement', 'make it work']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('double down', 'corporate', 'high', ARRAY['commit to', 'focus on', 'invest more in']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('level up', 'corporate', 'high', ARRAY['get better at', 'improve', 'grow']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('net-net', 'corporate', 'high', ARRAY['the point is', 'bottom line', 'in short']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('swim lane', 'corporate', 'high', ARRAY['responsibility', 'area of ownership', 'role']);

-- =============================================================================
-- Category 2: opener (30 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In today''s', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In today''s fast-paced world', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In today''s fast-paced environment', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In today''s rapidly evolving', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here''s the thing', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let me break it down', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''ve been thinking about', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('It''s important to note', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('It''s worth mentioning', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let''s explore', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let''s unpack', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I want to share', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m excited to announce', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The truth is', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The reality is', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('As we all know', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In a world where', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Now more than ever', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In an era of', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The landscape is changing', 'opener', 'high', ARRAY['name the change', 'specify what changed', 'describe the shift']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Whether you''re X or Y', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('If you''re reading this', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I need to talk about', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('We need to talk about', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let''s dive in', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Welcome to', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Are you ready to', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I want to talk about', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('What if I told you', 'opener', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Imagine a world where', 'opener', 'high', ARRAY[NULL]);

-- =============================================================================
-- Category 3: transition (30 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('furthermore', 'transition', 'high', ARRAY['also', 'and', 'plus']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('moreover', 'transition', 'high', ARRAY['also', 'and', 'on top of that']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('nevertheless', 'transition', 'high', ARRAY['still', 'even so', 'yet']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('consequently', 'transition', 'high', ARRAY['so', 'as a result', 'because of this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('additionally', 'transition', 'high', ARRAY['also', 'and', 'plus']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('subsequently', 'transition', 'high', ARRAY['then', 'after that', 'next']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in conclusion', 'transition', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in summary', 'transition', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('to summarize', 'transition', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('to conclude', 'transition', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in essence', 'transition', 'high', ARRAY['basically', 'at its simplest', 'put simply']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('ultimately', 'transition', 'high', ARRAY['in the end', 'finally', 'when it matters']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('hence', 'transition', 'high', ARRAY['so', 'that''s why', 'because of this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('thus', 'transition', 'high', ARRAY['so', 'that''s why', 'because of this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('therefore', 'transition', 'high', ARRAY['so', 'that''s why', 'which means']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('however', 'transition', 'high', ARRAY['but', 'yet', 'still']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('notwithstanding', 'transition', 'high', ARRAY['despite', 'even with', 'regardless of']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('albeit', 'transition', 'high', ARRAY['though', 'even if', 'although']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('henceforth', 'transition', 'high', ARRAY['from now on', 'going ahead', 'starting now']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('heretofore', 'transition', 'high', ARRAY['until now', 'up to this point', 'before this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in light of', 'transition', 'high', ARRAY['given', 'considering', 'because of']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('given the foregoing', 'transition', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('by the same token', 'transition', 'high', ARRAY['similarly', 'in the same way', 'likewise']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('on the other hand', 'transition', 'high', ARRAY['but', 'yet', 'alternatively']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('that being said', 'transition', 'high', ARRAY['but', 'still', 'even so']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('having said that', 'transition', 'high', ARRAY['but', 'still', 'even so']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it follows that', 'transition', 'high', ARRAY['so', 'which means', 'that''s why']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('as a result', 'transition', 'high', ARRAY['so', 'because of this', 'which led to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('to that end', 'transition', 'high', ARRAY['so', 'for that reason', 'to make that happen']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('be that as it may', 'transition', 'high', ARRAY['still', 'even so', 'regardless']);

-- =============================================================================
-- Category 4: conclusion (22 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The bottom line', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Needless to say', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('At the end of the day', 'conclusion', 'high', ARRAY['in the end', 'when it counts', 'what matters is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Moving forward', 'conclusion', 'high', ARRAY['next', 'from here', 'after this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('In conclusion', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('As a final thought', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('To wrap things up', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I hope this was helpful', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I hope you found this valuable', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Feel free to reach out', 'conclusion', 'high', ARRAY['DM me', 'message me', 'reach out about X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Don''t hesitate to contact me', 'conclusion', 'high', ARRAY['DM me', 'message me', 'reach out about X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Thank you for reading', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I appreciate your time', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Stay tuned for more', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Until next time', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('That''s a wrap', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('When all is said and done', 'conclusion', 'high', ARRAY['in the end', 'ultimately', 'when it matters']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('All things considered', 'conclusion', 'high', ARRAY['given all of this', 'weighing everything', 'looking at the full picture']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I hope this resonates', 'conclusion', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let me know your thoughts', 'conclusion', 'high', ARRAY['ask a specific question', 'what would you change about X', 'have you tried X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('What do you think?', 'conclusion', 'high', ARRAY['ask a specific question', 'what would you do differently', 'have you seen this work']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Food for thought', 'conclusion', 'high', ARRAY[NULL]);

-- =============================================================================
-- Category 5: intensifier (32 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('multifaceted', 'intensifier', 'high', ARRAY['complex', 'layered', 'detailed']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('unprecedented', 'intensifier', 'high', ARRAY['new', 'never seen before', 'first of its kind']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('revolutionary', 'intensifier', 'high', ARRAY['new', 'different', 'a big change']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('transformative', 'intensifier', 'high', ARRAY['meaningful', 'significant', 'changes how we']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('game-changing', 'intensifier', 'high', ARRAY['significant', 'a real shift', 'changes the outcome']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('game-changer', 'intensifier', 'high', ARRAY['turning point', 'major shift', 'breakthrough']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('mind-blowing', 'intensifier', 'high', ARRAY['surprising', 'unexpected', 'hard to believe']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('groundbreaking', 'intensifier', 'high', ARRAY['new', 'first of its kind', 'original']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('exciting', 'intensifier', 'high', ARRAY['show why it matters', 'describe the impact', 'explain the benefit']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('amazing', 'intensifier', 'high', ARRAY['show what''s good', 'describe what impressed you', 'be specific']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('incredible', 'intensifier', 'high', ARRAY['show what''s notable', 'describe what stood out', 'be specific']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('remarkable', 'intensifier', 'high', ARRAY['worth noting', 'notable', 'stood out']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('exceptional', 'intensifier', 'high', ARRAY['strong', 'above average', 'standout']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('extraordinary', 'intensifier', 'high', ARRAY['rare', 'unusual', 'uncommon']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('invaluable', 'intensifier', 'high', ARRAY['essential', 'critical', 'necessary']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('pivotal', 'intensifier', 'high', ARRAY['key', 'central', 'important']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('crucial', 'intensifier', 'high', ARRAY['key', 'important', 'needed']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('significant', 'intensifier', 'high', ARRAY['real', 'measurable', 'noticeable']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('compelling', 'intensifier', 'high', ARRAY['strong', 'convincing', 'clear']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('comprehensive', 'intensifier', 'high', ARRAY['complete', 'full', 'thorough']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('innovative', 'intensifier', 'high', ARRAY['new', 'creative', 'original']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('disruptive', 'intensifier', 'high', ARRAY['different', 'unconventional', 'breaks the mold']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('world-class', 'intensifier', 'high', ARRAY['top-tier', 'elite', 'among the best']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('next-generation', 'intensifier', 'high', ARRAY['newer', 'updated', 'improved']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('best-of-breed', 'intensifier', 'high', ARRAY['best available', 'top option', 'leading choice']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('bleeding-edge', 'intensifier', 'high', ARRAY['newest', 'latest', 'experimental']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('paradigm-shifting', 'intensifier', 'high', ARRAY['changes the approach', 'redefines how we', 'shifts the way']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('mission-driven', 'intensifier', 'high', ARRAY['purpose-built', 'goal-oriented', 'focused on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('value-add', 'intensifier', 'high', ARRAY['added benefit', 'bonus', 'extra value']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('synergistic', 'intensifier', 'high', ARRAY['combined', 'complementary', 'working together']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('best practice', 'intensifier', 'high', ARRAY['proven approach', 'what works', 'effective method']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('industry-leading', 'intensifier', 'high', ARRAY['top', 'leading', 'ahead of most']);

-- =============================================================================
-- Category 6: ai_tell (40 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('delve into', 'ai_tell', 'high', ARRAY['look at', 'examine', 'explore']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('unpack', 'ai_tell', 'high', ARRAY['break down', 'explain', 'walk through']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('dive deep', 'ai_tell', 'high', ARRAY['look closely at', 'examine in detail', 'dig into']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('dive in', 'ai_tell', 'high', ARRAY['start', 'begin', 'get into']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('testament to', 'ai_tell', 'high', ARRAY['proof of', 'evidence of', 'shows']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it goes without saying', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('rest assured', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a tapestry of', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('navigating the complexities', 'ai_tell', 'high', ARRAY['working through', 'handling', 'dealing with']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in the realm of', 'ai_tell', 'high', ARRAY['in', 'within', 'when it comes to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('stands at the forefront', 'ai_tell', 'high', ARRAY['leads', 'is ahead', 'is first']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('plays a crucial role', 'ai_tell', 'high', ARRAY['matters', 'is important', 'is key']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is worth noting', 'ai_tell', 'high', ARRAY['note:', 'keep in mind', 'worth knowing']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('shed light on', 'ai_tell', 'high', ARRAY['explain', 'clarify', 'show']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in conclusion it is clear', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('when it comes to', 'ai_tell', 'high', ARRAY['for', 'with', 'regarding']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a myriad of', 'ai_tell', 'high', ARRAY['many', 'lots of', 'dozens of']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('nuanced', 'ai_tell', 'high', ARRAY['specific', 'detailed', 'subtle']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('undeniable', 'ai_tell', 'high', ARRAY['clear', 'obvious', 'plain']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('pave the way', 'ai_tell', 'high', ARRAY['open the door to', 'make room for', 'enable']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('foster', 'ai_tell', 'high', ARRAY['build', 'grow', 'encourage']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('empower', 'ai_tell', 'high', ARRAY['help', 'enable', 'give tools to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('unlock', 'ai_tell', 'high', ARRAY['access', 'open up', 'make available']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('seamlessly', 'ai_tell', 'high', ARRAY['smoothly', 'easily', 'without friction']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('intrinsically', 'ai_tell', 'high', ARRAY['naturally', 'by nature', 'inherently']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('leveraging AI', 'ai_tell', 'high', ARRAY['using AI', 'with AI', 'through AI']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it''s no secret that', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('the elephant in the room', 'ai_tell', 'high', ARRAY['the obvious problem', 'the thing no one mentions', 'the big issue']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('resonate with', 'ai_tell', 'high', ARRAY['connect with', 'relate to', 'feel relevant to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('at its core', 'ai_tell', 'high', ARRAY['really', 'fundamentally', 'at the heart of it']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('stands as', 'ai_tell', 'high', ARRAY['is', 'remains', 'works as']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('serves as', 'ai_tell', 'high', ARRAY['is', 'works as', 'acts like']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('acts as', 'ai_tell', 'high', ARRAY['is', 'works as', 'functions like']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('functions as', 'ai_tell', 'high', ARRAY['is', 'works as', 'operates like']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a deep understanding', 'ai_tell', 'high', ARRAY['real understanding', 'solid grasp', 'clear knowledge']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('rich tapestry', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a beacon of', 'ai_tell', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('an array of', 'ai_tell', 'high', ARRAY['several', 'a range of', 'multiple']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a plethora of', 'ai_tell', 'high', ARRAY['many', 'plenty of', 'lots of']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a slew of', 'ai_tell', 'high', ARRAY['many', 'a lot of', 'numerous']);

-- =============================================================================
-- Category 7: filler (24 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('we (solo author)', 'filler', 'high', ARRAY['I', 'my']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('our team (solo)', 'filler', 'high', ARRAY['my team', 'the team', 'my group']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('our community', 'filler', 'high', ARRAY['people here', 'members', 'the group']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('community (generic)', 'filler', 'high', ARRAY['people', 'group', 'audience']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('from a X perspective', 'filler', 'high', ARRAY['as a X', 'in my role as X', 'speaking as X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in terms of', 'filler', 'high', ARRAY['for', 'about', 'regarding']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('with regards to', 'filler', 'high', ARRAY['about', 'on', 'regarding']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('as it pertains to', 'filler', 'high', ARRAY['about', 'for', 'related to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('at this juncture', 'filler', 'high', ARRAY['now', 'right now', 'at this point']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in the current climate', 'filler', 'high', ARRAY['right now', 'today', 'these days']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in today''s landscape', 'filler', 'high', ARRAY['now', 'today', 'currently']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('things (unspecified)', 'filler', 'high', ARRAY['name the thing', 'be specific', 'say what you mean']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('stuff (unspecified)', 'filler', 'high', ARRAY['name the thing', 'be specific', 'say what you mean']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('very', 'filler', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('really', 'filler', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('quite', 'filler', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('somewhat', 'filler', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a little bit', 'filler', 'high', ARRAY['slightly', 'a bit', 'marginally']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a number of', 'filler', 'high', ARRAY['several', 'a few', 'multiple']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a great deal of', 'filler', 'high', ARRAY['a lot of', 'plenty of', 'significant']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('on a daily basis', 'filler', 'high', ARRAY['every day', 'daily', 'each day']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('at this point in time', 'filler', 'high', ARRAY['now', 'right now', 'currently']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('due to the fact that', 'filler', 'high', ARRAY['because', 'since', 'as']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('for all intents and purposes', 'filler', 'high', ARRAY['effectively', 'practically', 'in practice']);

-- =============================================================================
-- Category 8: hedging (28 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('tends to', 'hedging', 'high', ARRAY['often does', 'usually', 'frequently']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('seems to', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('appears to', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('might be', 'hedging', 'high', ARRAY['is', 'could be', 'or don''t say it']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('could potentially', 'hedging', 'high', ARRAY['can', 'could', 'is able to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it''s possible that', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('may or may not', 'hedging', 'high', ARRAY['pick one', 'decide and state', 'commit to a position']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('to some extent', 'hedging', 'high', ARRAY['partly', 'in part', 'partially']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in some ways', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it could be argued', 'hedging', 'high', ARRAY['I''d argue', 'I believe', 'my take is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('there''s a case to be made', 'hedging', 'high', ARRAY['here''s the case', 'I''d argue', 'the argument is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('one could say', 'hedging', 'high', ARRAY['I''d say', 'I think', 'my view is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it''s fair to say', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it''s reasonable to assume', 'hedging', 'high', ARRAY['I''d assume', 'I believe', 'it''s likely']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('more or less', 'hedging', 'high', ARRAY['roughly', 'about', 'approximately']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('arguably', 'hedging', 'high', ARRAY['make the argument', 'I''d argue', 'the case is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('perhaps', 'hedging', 'high', ARRAY['maybe', 'possibly', 'it could be']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is believed that', 'hedging', 'high', ARRAY['I believe', 'many believe', 'the consensus is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it can be said that', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('to a certain degree', 'hedging', 'high', ARRAY['partly', 'in part', 'to some degree']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in a sense', 'hedging', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it''s not entirely clear', 'hedging', 'high', ARRAY['it''s unclear', 'we don''t know', 'the answer isn''t clear']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('there is some evidence', 'hedging', 'high', ARRAY['the evidence shows', 'data suggests', 'research shows']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is generally accepted', 'hedging', 'high', ARRAY['most people agree', 'the consensus is', 'widely agreed']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is widely recognized', 'hedging', 'high', ARRAY['everyone knows', 'it''s well known', 'widely understood']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('some would argue', 'hedging', 'high', ARRAY['critics say', 'skeptics point out', 'others believe']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('the jury is still out', 'hedging', 'high', ARRAY['we don''t know yet', 'it''s undecided', 'no one agrees']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('only time will tell', 'hedging', 'high', ARRAY['we''ll see', 'it remains to be seen', 'we''ll find out']);

-- =============================================================================
-- Category 9: academic (28 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in accordance with', 'academic', 'high', ARRAY['following', 'per', 'based on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('with respect to', 'academic', 'high', ARRAY['about', 'regarding', 'on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in the context of', 'academic', 'high', ARRAY['in', 'within', 'during']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is imperative', 'academic', 'high', ARRAY['you need to', 'you must', 'it''s critical to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is essential', 'academic', 'high', ARRAY['you must', 'you need to', 'it''s necessary to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is crucial', 'academic', 'high', ARRAY['you must', 'you need to', 'it''s important to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it is paramount', 'academic', 'high', ARRAY['the most important thing is', 'above all', 'the priority is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in order to', 'academic', 'high', ARRAY['to', 'so you can', 'for']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('for the purpose of', 'academic', 'high', ARRAY['to', 'for', 'so that']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in the event that', 'academic', 'high', ARRAY['if', 'when', 'should']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('prior to', 'academic', 'high', ARRAY['before', 'ahead of', 'earlier than']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('subsequent to', 'academic', 'high', ARRAY['after', 'following', 'once']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in conjunction with', 'academic', 'high', ARRAY['with', 'along with', 'together with']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('on behalf of', 'academic', 'high', ARRAY['for', 'representing', 'speaking for']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('with the aim of', 'academic', 'high', ARRAY['to', 'aiming to', 'in hopes of']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('pertaining to', 'academic', 'high', ARRAY['about', 'related to', 'on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('commensurate with', 'academic', 'high', ARRAY['matching', 'in line with', 'proportional to']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('predicated on', 'academic', 'high', ARRAY['based on', 'built on', 'depending on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('aforementioned', 'academic', 'high', ARRAY['mentioned earlier', 'the one I mentioned', 'that']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('therein', 'academic', 'high', ARRAY['in it', 'inside', 'within']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('whereby', 'academic', 'high', ARRAY['where', 'through which', 'so that']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('wherein', 'academic', 'high', ARRAY['where', 'in which', 'inside']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it should be emphasized', 'academic', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it must be acknowledged', 'academic', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('it cannot be overstated', 'academic', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('a considerable amount of', 'academic', 'high', ARRAY['a lot of', 'plenty of', 'substantial']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('with regard to the matter of', 'academic', 'high', ARRAY['about', 'regarding', 'on']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('in the interest of', 'academic', 'high', ARRAY['for', 'to support', 'in favor of']);

-- =============================================================================
-- Category 10: emotional (20 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m so excited to', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m thrilled to announce', 'emotional', 'high', ARRAY['just announce it', 'announcing:', 'here it is:']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m honored to', 'emotional', 'high', ARRAY['just state it', 'state the fact', 'say what happened']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m humbled by', 'emotional', 'high', ARRAY['just state it', 'say what happened', 'describe the situation']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m passionate about', 'emotional', 'high', ARRAY['show passion through results', 'demonstrate with examples', 'prove it with work']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m blessed to', 'emotional', 'high', ARRAY['just state it', 'say what happened', 'describe the opportunity']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m grateful for', 'emotional', 'high', ARRAY['be specific one line', 'thank a specific person', 'name what you appreciate']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I couldn''t be more proud', 'emotional', 'high', ARRAY['I''m proud of this', 'proud of the team', 'this is good work']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('My heart goes out to', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('This hit different', 'emotional', 'high', ARRAY['say what hit and why', 'explain the impact', 'describe what changed']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m beyond grateful', 'emotional', 'high', ARRAY['thank you to specific person', 'thanks to [name]', 'I appreciate [specific thing]']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I can''t stress enough', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Words cannot express', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('It fills me with joy', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('This means the world to me', 'emotional', 'high', ARRAY['say what it means', 'explain the significance', 'describe the impact']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''m incredibly proud', 'emotional', 'high', ARRAY['I''m proud', 'proud of this', 'this is strong work']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Absolutely blown away', 'emotional', 'high', ARRAY['say what surprised you', 'describe what stood out', 'explain the surprise']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Super pumped about', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Beyond excited', 'emotional', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Deeply moved by', 'emotional', 'high', ARRAY['say what moved you', 'describe the moment', 'explain why it mattered']);

-- =============================================================================
-- Category 11: linkedin_pattern (22 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Agree? 🤝', 'linkedin_pattern', 'high', ARRAY['ask specific question', 'what would you change', 'how do you handle X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Thoughts? 👇', 'linkedin_pattern', 'high', ARRAY['ask specific question', 'what''s your experience with X', 'how would you approach X']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Comment below 👇', 'linkedin_pattern', 'high', ARRAY['ask a question that invites real answer', 'what would you add', 'share your experience']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Repost ♻️ if you agree', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Follow for more', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Save this for later 🔖', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Hit like if you', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Tag someone who needs this', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Drop a 🔥 if you agree', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Share this with someone who', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here are X things I learned', 'linkedin_pattern', 'high', ARRAY['start with the first thing', 'lead with the strongest insight', 'open with the lesson']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here are X tips for', 'linkedin_pattern', 'high', ARRAY['start with strongest tip', 'lead with the best advice', 'open with the most useful one']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here are X ways to', 'linkedin_pattern', 'high', ARRAY['start with best way', 'lead with the most effective', 'open with what works']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('X things I wish I knew', 'linkedin_pattern', 'high', ARRAY['start with most important', 'lead with the biggest lesson', 'open with the one that matters most']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('A thread 🧵', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Hot take:', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Unpopular opinion: (generic)', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('PSA:', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Read that again.', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let that sink in.', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Say it louder for the people in the back', 'linkedin_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('This. 👆', 'linkedin_pattern', 'high', ARRAY[NULL]);

-- =============================================================================
-- Category 12: structure_pattern (22 phrases)
-- =============================================================================

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The key is', 'structure_pattern', 'high', ARRAY['state it directly', 'say what matters', 'just say it']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The secret is', 'structure_pattern', 'high', ARRAY['state directly', 'just say it', 'here''s what works']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The answer is simple', 'structure_pattern', 'high', ARRAY['just give the answer', 'state it', 'here it is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('It all comes down to', 'structure_pattern', 'high', ARRAY['say what it comes down to', 'state the core point', 'the main thing is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Picture this:', 'structure_pattern', 'high', ARRAY['describe the scene', 'set the context', 'here''s the situation']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here''s what most people miss', 'structure_pattern', 'high', ARRAY['say what they miss directly', 'the overlooked part is', 'most people skip']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('But here''s the thing', 'structure_pattern', 'high', ARRAY['say the thing', 'state the point', 'but']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('And that''s the point', 'structure_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let me explain', 'structure_pattern', 'high', ARRAY['just explain', 'here''s why', 'the reason is']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Allow me to elaborate', 'structure_pattern', 'high', ARRAY['just elaborate', 'to be specific', 'in detail']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Not just X but Y', 'structure_pattern', 'high', ARRAY['pick stronger framing', 'lead with Y', 'focus on Y']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('It''s not about X it''s about Y', 'structure_pattern', 'high', ARRAY['just say it''s about Y', 'focus on Y', 'Y matters most']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('The real question is', 'structure_pattern', 'high', ARRAY['ask the question', 'here''s the question', 'the question:']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here''s what nobody tells you', 'structure_pattern', 'high', ARRAY['just say it', 'state the insight', 'the overlooked truth']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Spoiler alert:', 'structure_pattern', 'high', ARRAY[NULL]);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Plot twist:', 'structure_pattern', 'high', ARRAY['use only if actual reversal', 'but then', 'the opposite happened']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Pro tip:', 'structure_pattern', 'high', ARRAY['just give the tip', 'one thing that helps', 'try this']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here''s a framework', 'structure_pattern', 'high', ARRAY['just share it', 'the framework:', 'here''s how I think about it']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Let me paint a picture', 'structure_pattern', 'high', ARRAY['just paint it', 'here''s the scene', 'imagine']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Here''s my take', 'structure_pattern', 'high', ARRAY['my take: then state position', 'I think', 'my view:']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('I''ll keep this short', 'structure_pattern', 'high', ARRAY['just keep it short', 'briefly:', 'in short']);

INSERT INTO ls_ai_phrases_blocklist (phrase, category, severity, replacement_suggestions) VALUES
('Buckle up', 'structure_pattern', 'high', ARRAY[NULL]);

COMMIT;

-- =============================================================================
-- Summary: Total phrases per category
-- =============================================================================
-- corporate:         48 phrases
-- opener:            30 phrases
-- transition:        30 phrases
-- conclusion:        22 phrases
-- intensifier:       32 phrases
-- ai_tell:           40 phrases
-- filler:            24 phrases
-- hedging:           28 phrases
-- academic:          28 phrases
-- emotional:         20 phrases
-- linkedin_pattern:  22 phrases
-- structure_pattern: 22 phrases
-- ---------------------------------
-- TOTAL:            346 phrases
-- =============================================================================

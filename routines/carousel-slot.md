# Clerion carousel: one slot per run

You make ONE carousel for Clerion and schedule it through Zernio on TikTok @clerionhq (with a hand-picked track) and Instagram @clerionhq. Ten separate scheduled tasks each run this playbook for one slot, one after another, about 45 minutes apart. Your slot is named in the task prompt. Finish without asking questions. Nobody is watching.

Time budget: 40 minutes. Note the start time. At 35 minutes, stop starting new work: if the carousel is rendered and pushed, schedule it; otherwise report the slot as skipped. Never skip the report rules in step 9.

## 0. Slots and post date
Post date D = tomorrow in New York (work it out with `TZ=America/New_York date`).
- US slots (America/New_York): us-1 07:00, us-2 10:00, us-3 13:00, us-4 17:00, us-5 21:00.
- EU slots (Europe/Berlin): eu-1 07:00, eu-2 10:00, eu-3 15:00, eu-4 18:00, eu-5 21:00.
- Run order (by UTC slot time): eu-1, eu-2, us-1, eu-3, us-2, eu-4, us-3, eu-5, us-4, us-5.
Step 2b may move a slot by up to 2 hours. Convert all ten to UTC: no two may be under 60 minutes apart (both regions post to the same two accounts). If two collide (around daylight-saving changes), move the EU one 1 hour later and check again.
Your carousel goes out on TikTok and Instagram at the same slot time. If your slot time is less than 90 minutes from now when you reach step 8, skip it and report it.
Volume: if log.csv shows the account running at 6 a day (step 2b), only us-2, us-3, us-4, eu-2, eu-3, eu-4 run. Any other slot: do step 8b only, then stop without a notification.

## 1. Get the repo
Call add_repo for MinuraKariyawasam/social-imgs with push access. Run git clone --depth 1 https://github.com/MinuraKariyawasam/social-imgs. If the clone already exists in the working directory, git checkout main and git pull. It holds:
- templates/cover.html, inner.html, closer.html, base.css: the blue-board design (1080x1350). Never change them. templates/classic/ is the old white design; never use it for new posts.
- scripts/render.py: renders all slides from a spec JSON into "outdir". scripts/crop.py crops paintings (render.py calls it).
- examples/blueboard-spec.json and examples/blueboard/: a complete working spec and its rendered slides. Copy its structure exactly.
- library/: public-domain paintings. library/library.csv has file, mood, use_for and crop focus. library/paintings.csv has title, artist, source.
- log.csv: every carousel already made (post_date, region, local_time, timezone, title, cover, post_id (TikTok), ig_post_id (Instagram), paintings). For new rows the cover column holds the cover painting file.
- plans/<D>.csv: the day plan shared by the ten runs (step 3). Columns: slot, region, local_time, pillar, title, hook, keyword, guide_url, cover, paintings (";"), track, status (planned, claimed, scheduled, skipped, failed), note.
- insights.md: running analytics notes (create if missing). comment-keywords.csv and replied.csv: see step 8b.
- posts/: existing folders hold live images. Never modify, overwrite or delete an existing folder. Your folder is posts/<D>-<slot>/ ("outdir"); if it exists, use -v2, -v3 and so on. Ignore posts/2026-10-14-nordic/.

Git discipline (other runs share this repo): always `git pull --rebase` right before every commit, commit only your own files plus your own rows, and if a push is rejected, pull --rebase and push again (up to 3 times). Never force-push.

## 2. Check what's already scheduled
Call Zernio posts_list with status scheduled (limit 100) and posts_get on each to read platform and time.
- Your slot is done on a platform if log.csv has a row for D, your region and your slot's local_time with that platform's id, or Zernio has a post on that platform scheduled on D within 45 minutes of your slot time.
- Both done: do step 8b, then stop without a notification. One done: schedule just the missing platform, reusing that row's folder and caption.
- A Zernio post on D that isn't in log.csv: don't touch it, treat its time as taken for the 60-minute rule, and mention it in your report.

## 2b. Read what's working (every run, before choosing anything)
- analytics_get_analytics for TikTok (account_id 6ace1f28b762e0de33b023d6, platform tiktok) and Instagram (account_id 6ace5709d03cba011742d506, platform instagram), from_date 45 days ago, limit 100, page through. If the result is too big, save it and summarise with jq or python.
- analytics_get_best_time_to_post for each account.
- Match posts to log.csv by post_id or ig_post_id for region, title, local hour, weekday, cover, paintings. Unmatched posts count only for account-wide signals.
- Only score posts published 48+ hours ago.

Score: reach = views (TikTok) or reach/impressions (Instagram). viral_rate = (shares + saves) / reach. viral_score = rank of reach + rank of viral_rate + 0.5 x rank of comments/reach, within one platform. Never compare raw TikTok numbers with raw Instagram ones.

Tag each scored post: pillar P1 to P6 (from the "pillars" list in insights.md or plans/; for posts before 2026-10-16 assign from the title), theme, title pattern and intensity word, hook type (keep-it vs call-out), CTA type (guide vs engagement), design (blueboard from 2026-10-15, classic before), painting moods, region, local hour, weekday.

Decide (small samples lie, so these are strict):
- Under 6 scored posts in total: not enough data. Use queue order and default hours.
- Pillar: compare pillars by median viral_score per region once each has 2+ scored posts.
- Topic: a theme or pattern is winning with 2+ scored posts and median viral_score in the top third, losing with 2+ in the bottom third. Winning first, then not-losing, then losing. Keep at least one test of a different theme per region per day.
- Hook: when one type beats the other with 2+ posts each, use it on most posts, but keep at least one of each type per day.
- CTA: once both types have 4+ scored posts, compare median comments/reach and note the winner.
- Design: once blueboard has 10+ scored posts, compare its median viral_score per platform with classic and report it. Keep blueboard.
- Time: once a region has 10+ scored posts across 4+ hours, you may move your slot up to 2 hours toward a clearly better hour (2+ posts there, top third). With less data, only to best_time_to_post's best hour for that weekday if within 2 hours of default. Never within 2 hours of another slot of your region; always keep 60-minute UTC spacing.
- Volume: once there are 3+ days at 10 carousels a day (2-a-day days are 2026-10-13 and earlier), compare average reach per post on 10-a-day days against 2-a-day days per platform. If it dropped by more than half on either, the day plan switches to 6 a day (us-2, us-3, us-4, eu-2, eu-3, eu-4). Once log.csv shows 6 a day, stay at 6.
- Paintings: a mood that clearly wins (2+ posts, top third) is preferred for the cover and the harshest-truth slide.
- Region: if one region's median reach is under a third of the other's over 6+ posts each, flag it.
- Never break steps 3 to 5 to chase a number.

Write it down in insights.md:
- If you are the run that creates the day plan (step 3), append a dated section "## <D> analytics" with a small table (title, region, slot, platform, reach, viral_rate, viral_score), winners and losers (pillars, themes, patterns, hooks, CTAs, design, hours, moods) and the plan decisions and why.
- Every other run appends one or two lines under that section: "<slot>: <what changed in the numbers since the plan, if anything> -> <kept plan | changed X because Y>".
Keep insights.md under about 300 lines by condensing older sections into a "standing findings" list at the top.

## 3. The day plan, and your title
### If plans/<D>.csv does not exist (normally the eu-1 run): make the whole day plan
Plan all slots (10, or 6 at 6 a day) so the day stays varied, then commit and push plans/<D>.csv before you start writing your own carousel. Each row: slot, region, local_time (after any 2b move), pillar, title, hook, keyword (reserved, unique across the day, or "engagement"), guide_url (only if you opened it today and it loads), cover painting, five inner paintings (step 5), status "planned".
Re-check: pull, and if another run created plans/<D>.csv meanwhile, use theirs and discard yours.

Pillars (every carousel belongs to one):
- P1 where customers come from: AI assistant traffic (ChatGPT, Claude, Perplexity, Gemini, Copilot), which source brings paying customers, revenue by source.
- P2 what they do on the site: user flows, where visitors leave, funnels to sign-ups and checkouts, exit reasons, rage clicks.
- P3 whether the site is working: how AI assistants read your site (titles, headings, meta, schema), speed and Core Web Vitals, script errors, whether a deploy broke something.
- P4 what to do about it: reading analytics fast, finding the one fix to make first, spotting what changed, investor update numbers.
- P5 SI and AI founder life: superintelligence, AI search, founder habits (US); european law, funding and selling across europe (EU).
- P6 growth and distribution for AI founders: growing on X, build in public, launches (Product Hunt, Show HN), Reddit, cold DMs, newsletters and press, first users.
Daily mix per region: one P5, one P6, three of P1 to P4. The website pillar left out rotates: skip the one with the most carousels for that region over the last 3 days (pillars from insights.md/plans; tie: skip the higher number). Strongest pick (2b) in the best hour. A winning pillar may take a second slot from the weakest, but P5 and P6 keep a slot every day and each of P1 to P4 runs at least once every two days.
For each slot take the first unused title from that pillar's queue for that region (skip anything in log.csv or that repeats a log.csv topic from the last 14 days, even reworded).

US queues:
P1: 1. 5 niche ways to become the founder chatgpt sends customers to | (save them) 2. 5 niche signs your best customers came from perplexity, not google | (good luck) 3. 5 niche ways to know which channel actually pays you | (copy them)
P2: 1. 5 niche things that will make you terrifyingly good at finding where users quit | (you're probably doing none of them) 2. 5 niche habits of founders who know their funnel by heart | (copy them) 3. 5 niche ways to turn rage clicks into revenue | (fix them tonight) 4. 5 niche ways to find what your signup page is hiding | (screenshot this)
P3: 1. 5 niche ways to make your site readable by claude and chatgpt | (save them) 2. 5 niche things that will make you annoyingly good at catching bugs before users do | (copy them) 3. 5 niche habits of founders who never ship a broken deploy | (good luck) 4. 5 niche ways to become the founder whose site loads in under a second | (save for later)
P4: 1. 5 niche habits of founders who make one fix a day | (copy them) 2. 5 niche ways to read your analytics in 5 minutes, not 50 | (save them) 3. 5 niche things that will make you disgustingly good at investor updates | (screenshot this) 4. 5 niche signs you're staring at dashboards instead of fixing things | (you're probably doing none of them)
P5: 1. 5 niche things superintelligence can't see on your website | (fix them tonight) 2. 5 niche free tools that will make you disgustingly good at seo in the si era | (save for later)
P6: 1. 5 niche habits of ai founders who grow on x without going viral | (copy them) 2. 5 niche ways to become the founder who launches on product hunt and wins the day | (save them) 3. 5 niche numbers ai founders should post every week | (screenshot this) 4. 5 niche ways to get your first 100 users from reddit without getting banned | (save them) 5. 5 niche things that will make you dangerously good at writing x threads | (screenshot this) 6. 5 niche things that will make you terrifyingly good at show hn posts | (you're probably doing none of them) 7. 5 niche ways to build in public without giving away the moat | (save them) 8. 5 niche signs your x account is talking to founders, not customers | (good luck) 9. 5 niche things that will make you annoyingly good at cold dms | (good luck) 10. 5 niche ways to become the founder newsletters write about | (screenshot this) 11. 5 niche ways to turn one x post into 10 signups | (save them) 12. 5 niche habits of founders whose revenue screenshots get shared | (copy them) 13. 5 niche ways to launch the same product 5 times | (copy them) 14. 5 niche signs your ai wrapper needs a distribution plan, not a feature | (you're probably doing none of them)

EU queues:
P1: 1. 5 niche ways to find which country pays you in euros | (save them) 2. 5 niche ways to become the founder european chatgpt users find first | (screenshot this)
P2: 1. 5 niche ways to fix a checkout that loses half of europe | (good luck) 2. 5 niche things that will make you dangerously good at reading users in 5 languages | (copy them)
P3: 1. 5 niche ways to stay fast for users from lisbon to helsinki | (screenshot this) 2. 5 niche ways to become the founder whose analytics gdpr can't touch | (save them)
P4: 1. 5 niche numbers every european investor update needs | (save them) 2. 5 niche habits of european founders who fix one thing a day | (copy them)
P5: no queued titles; write new ones.
P6: 1. 5 niche ways to grow on x when your audience is in 12 time zones | (save them) 2. 5 niche habits of european founders who launch to the us first | (copy them) 3. 5 niche ways to get press in europe without a pr agency | (save them)

Unused title ideas live in an "idea backlog" at the bottom of insights.md; draw from it before writing fresh ones, and add ideas you don't use.

### If plans/<D>.csv exists: take your row
Use your slot's row. You may change your own row's title (same pillar, not used anywhere in the plan or log.csv, same topic rules), time (2b rules) or paintings only if this run's analytics give a clear reason; write the reason in the note column and insights.md. Never change another slot's row. If your row is missing (plan made at 6 a day, or a slot added), build it yourself within the plan's pillar mix and the uniqueness rules. Set status "claimed", pull --rebase, commit and push the plan right away.

### Topic rules (always)
- Every carousel in a day has a different subject, different facts, different inner slides. Before writing, read every other row of the plan and every carousel already rendered for D (their spec.json): stay off their subjects.
- No topic from the last 14 days of log.csv, even reworded.
- An EU topic is never a copy of any US topic in log.csv or the US queue, and the other way round.
- EU topics matter more to a founder in Europe: european law (eu ai act, gdpr, dma, cookie consent), many countries and languages, euros and european pricing, european funding and grants, eu data residency.
- US topics are for US founders: US examples, US market, dollars.

New titles, formula, no exceptions:
- "[number] niche [things] that will make you [disgustingly | terrifyingly | dangerously | annoyingly] [smart | cracked | good at X]", or
- "[number] niche habits of superintelligent [founders | builders]" (EU may say "european founders"), or
- "[number] niche ways to [get / become / do X]", or
- "[number] niche signs [you're / your X] ...", "[number] niche habits of founders who [do X]", or "[number] niche numbers every [X] needs".
The title promises who the reader becomes; it never names a problem, a complaint or a product. Hook: 2 to 5 words in brackets that tell them to keep it or call them out, e.g. (save them), (copy them), (good luck), (you're probably doing none of them). Never a CTA or link in the hook.
Sources for new titles: P1 to P4 from getclerion.com feature pages and getclerion.com/resources (the slides teach the habit or fact, never the product). US P5 from getclerion.com/resources (newest first), leaning on SI and superintelligence. P6 from getclerion.com/resources plus platforms' own rules (X, Product Hunt, Hacker News, Reddit), founder write-ups with real numbers (attributed), reputable startup press; never invent follower, signup or revenue numbers; an EU P6 needs a europe angle. EU titles from getclerion.com/resources plus european news and official eu pages read today. Favour topics with a matching getclerion.com/resources article or feature page (they get a guide CTA).

## 4. Write the slides (blue-board design)
Do the research and writing yourself (no subagents), at most 10 page reads.
Exactly 3 colours (the templates handle them). Yellow on ONE word or phrase per slide only. Write all spec text in lowercase (the templates capitalise headlines). No em dashes. No emoji.
- 7 slides: cover, 5 inner slides, closer (6 inner when the title says 6).
- Cover: split the title into "sub" (the small lead-in, e.g. "5 niche ways to become") and "title" (the big headline). Wrap the headline's keyword in <span class="y">…</span>. "steps": one 1 to 2 word label per inner slide. "hook": the bracketed hook. "image": the cover painting.
- Inner slide: "title" of 2 to 4 words with the word that matters in <span class="hl">…</span>. "body": exactly two sentences, under 30 words; sentence one says what it is, sentence two is the uncomfortable truth. "label": a 1 to 3 word yellow tag that reacts to the slide (e.g. "€1m fine"). "image": the painting.
- Closer: "HEADLINE" two lines with <br> reframing the post, reframe word(s) in <span class="y">…</span>. "TONIGHT", "THIS_WEEK", "NEXT_WEEK": under about 35 characters each. "CTA" below. "NEXT_TITLE": a next title from the same region's queue or backlog, not used by any slot in today's plan.
- CTA: one line under 55 characters asking for a one-word comment, the word in <b>…</b> (renders as a yellow tag).
  - Guide CTA when a getclerion.com/resources article or a getclerion.com "learn about" page covers the topic in full (open it today, confirm it loads): "comment <b>KEYWORD</b> and we'll reply with the full guide". Use the keyword reserved in the plan (one short lowercase word, unique that day).
  - Engagement CTA otherwise: e.g. "comment <b>3</b> if slide 3 hit hardest", "comment <b>me</b> if you skip all five", "comment the <b>number</b> you'll fix first". Never promise a guide that doesn't exist.
  - The CTA is on the closer only.
- Never mention Clerion on any slide.
- US posts: US sources and data, dollars. EU posts: european sources first (eur-lex, european commission and ai act pages, eurostat, eic and eu funding pages, european data protection authorities, european studies and press), euros; a point with only a US source stays only if equally true in Europe.
- Every fact comes from a page read today (web search or getclerion.com/resources). Claims about SI, AGI or the SI executive order come only from Clerion's own articles. Never invent a statistic. Never give legal advice as fact: state what the law or regulator page says, with its date. If the topic can't be sourced properly, swap to the next unused title in the same pillar (update your plan row) rather than padding.

## 5. Images
Never search for, download, generate or draw an image. Only library/ paintings; skip rows whose mood is "retired". covers/ and brand/ belong to the old design; don't use them.
- Cover: a painting that plays the "person on the thumbnail": a single clear face or figure looking out, ideally judging or shock (Bronzino, Kramskoi, Ducreux, Hals portraits work best). Different from the carousel's inner paintings.
- Inner: one painting per slide by mood and use_for: shock or judging for the harshest truth, waiting for waiting or doing nothing, thinking for doing the work, tracking or writing, triumph for winning or getting rewarded. Deadpan reaction to the text. Closest mood if the right one ran out.
- Never the same painting twice in a carousel. Within one region on one day, never twice (check the plan and log.csv); a cover may repeat one from the other region that day, never in two carousels less than 6 hours apart. Otherwise prefer paintings used least recently in log.csv.
The day plan pre-assigns paintings this way; keep them unless a slide's mood no longer fits.

## 6. Render
In the clone: npm i geist; pip install playwright pillow --break-system-packages; playwright install chromium (skip any that's already there).
Spec in exactly the shape of examples/blueboard-spec.json: {"date": "<D>", "region": "us"|"eu", "outdir": "posts/<D>-<slot>", "cover": {"sub", "title", "steps", "hook", "image"}, "inner": [{"title", "body", "label", "image"}, ...], "closer": {"HEADLINE", "TONIGHT", "THIS_WEEK", "NEXT_WEEK", "CTA", "NEXT_TITLE"}}. Run python3 scripts/render.py <spec>.
Check the printed numbers, then open every PNG and look:
- Every slide: font true, img_loaded true (closer null is fine).
- Cover: title_clear true, boxes_ok true, font_px 84+ (else move words into "sub" or shorten step labels).
- Inner: body_ok true, font_px 76+ (else shorten the title).
- Closer: title_clear true, boxes_ok true, cta_lines 1.
- Faces or main figures in frame, yellow on exactly one word or phrase, nothing clipped or overlapping.
Fix by shortening words or swapping a painting, re-render. Save spec.json in the folder.

## 7. Publish the images
caption.txt in the folder, in this order:
1. the full title (sub + title, plain text)
2. blank line, one "track it tonight" step per inner slide (one concrete action each)
3. blank line, the closer's CTA in plain text (no tags, keyword in capitals, e.g. "comment GDPR and we'll reply with the full guide")
4. blank line, 3 to 5 hashtags (EU: at least one european, e.g. #eustartups, #europeanstartups, #founderseurope; prefer hashtags step 2b shows on top posts), then @getclerionhq once. Never @getclerion on its own.
5. blank line, then exactly:

Website intelligence for AI founders.

Web analytics, AI traffic, conversions, errors and speed from one script tag. Clerion finds the patterns in the data every day and tells you the one fix to make first.

Under 2,000 characters total; shorten the tonight steps if needed, never the CTA or the marketing block.
Commit your folder (slides, caption, spec) plus your insights.md lines, pull --rebase, push to main. Never commit node_modules or package files. Wait until every https://raw.githubusercontent.com/MinuraKariyawasam/social-imgs/main/<folder>/slide-0N.png returns 200 with an md5 matching the local file (cache can take 5 minutes) before scheduling.

## 8. Schedule via Zernio (TikTok, then Instagram)
Zernio only. Never Buffer. Never publish_now.
- TikTok @clerionhq accountId 6ace1f28b762e0de33b023d6; Instagram @clerionhq accountId 6ace5709d03cba011742d506.
- media_items (both): slide URLs in order, each {"type": "image", "url": <raw URL>, "altText": <slide text without html: cover = full title, inner = its title, closer = the headline>}.

TikTok: call_tool "posts_create_post" with content: the full title only; media_items; platforms: [{"platform": "tiktok", "accountId": "6ace1f28b762e0de33b023d6"}]; scheduled_for "<D>T<HH>:<MM>:00"; timezone "America/New_York" or "Europe/Berlin"; tiktok_settings: {"media_type": "photo", "description": <full caption.txt>, "privacy_level": "PUBLIC_TO_EVERYONE", "allow_comment": true, "auto_add_music": false, "musicSoundInfo": {"musicSoundId": <clip id>}, "commercialContentType": "none", "content_preview_confirmed": true, "express_consent_given": true}.
Music: never auto_add_music. call_tool "accounts_list_tik_tok_commercial_music" with account_id 6ace1f28b762e0de33b023d6, country_code "US" (US) or "DE" (EU). Pick a calm, premium, instrumental track (easy listening, new age, jazz, lo-fi or chill beats, soft electronic, classical, piano). Skip meme, comedy, novelty, holiday, romance or sexy, aggressive, vocal pop, non-English vocals (judge by name, artist, genre). Not used by any other slot in today's plan, and not used in the last 3 days (insights.md). Send clip.id as musicSoundId (id only when there's no clip; never commercialMusicId). Write the track into your plan row and insights.md. If the list can't be fetched, post with no track and say so.
Run the same arguments once with "dry_run": true first and fix anything it reports.

Instagram (separate post): validate_post with content = full caption.txt, media_items, platforms [{"platform": "instagram", "accountId": "6ace5709d03cba011742d506"}]; fix anything. Then call_tool "posts_create_post" with content = full caption.txt, media_items, that platform, same scheduled_for and timezone. No music on Instagram; expected.

After each, posts_get the new post and confirm its UTC time matches. For a guide CTA append one row per platform to comment-keywords.csv (post_date, slot, platform, Zernio post id, keyword, guide_url).
On an error, record the exact error and carry on with the other platform. On a rate limit, wait as asked and retry once. A daily posting limit on a platform: stop on that platform, keep the other.

## 8b. Answer keyword comments (every run)
For each comment-keywords.csv row with post_date in the last 7 days whose post is live: comments_get_inbox_post_comments (post_id = Zernio id, account_id = that platform's account), page through. For each comment containing the keyword (case-insensitive, whole word), not from @clerionhq and not in replied.csv, reply with comments_reply_to_inbox_post using comment_id:
- Instagram: "here's the full guide: <guide_url>" (vary the opening: "here you go:", "as promised:").
- TikTok (150-character cap): "here's the full guide: <guide_url>", shortened if needed.
Append each to replied.csv right after replying, and pull --rebase before committing (another run may have replied too; never reply to a comment id already in replied.csv after the pull). At most 30 replies per run. On a rate limit, wait, retry once, then stop replying.

## 9. Log and report
Append your row to log.csv: post_date, region, local_time (HH:MM), timezone, full title, cover painting, TikTok post_id (empty if failed), Instagram ig_post_id (empty if failed), inner paintings joined with ";". (If you only filled a missing platform, update that row instead.) Set your plan row status to scheduled, skipped or failed, with the track. Add "<D>, <slot>, <pillar>" to the "pillars" list in insights.md. Commit (log.csv, plans, insights.md, csv files), pull --rebase, push. Then delete node_modules, package.json and package-lock.json from the clone.

Notifications (PushNotification, summary inside <routine_summary> tags):
- If anything went wrong in your run (a platform failed, the slot was skipped, sourcing forced a swap you couldn't make, the repo or Zernio was unreachable): send one notification. First sentence: "<slot> <D>: <what failed>". Then the exact error and what you did.
- If you are the last slot that runs today (us-5, or us-4 at 6 a day): send the day summary even if all went well. First sentence: how many of the planned posts for D got scheduled (carousels x 2). Then one "what's working" and one "what's not" line from 2b (or "not enough data yet"), any time or topic change, the design comparison and volume check once they apply. Then one line per slot from plans/<D>.csv and log.csv: slot, pillar, title, time in its own timezone and Asia/Saigon, platforms (flag failures), TikTok track, CTA keyword or "engagement". Then how many keyword comments got replies today (count replied.csv rows dated today). End with anything cut, skipped or not done.
- Otherwise (your slot went fine and you're not last): no notification.

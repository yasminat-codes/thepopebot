# YouTube Skill — Error Recovery Reference

Full error table for `fetch_and_learn.py`. When a new error is encountered in the field, add a row here and bump the SKILL.md version.

---

## Error Table

| Error | Root Cause | What You See | Prevention | Recovery |
|-------|-----------|--------------|------------|---------|
| No subtitles found | No English captions (auto or manual) | Script outputs note with "> No captions available" message | Check video has CC badge before processing | Suggest `last30days` skill: "This video has no captions. You can research this topic with the `last30days` skill instead." |
| All AI providers failed | All 3 API keys missing, expired, or quota exhausted | `ERROR: All AI providers failed. Check API keys in .env.` | Validate keys work — see API-SETUP.md one-liners | Add/refresh keys in `.env`; verify with one-liner tests in API-SETUP.md |
| RSS parse error | Feed URL is malformed, not Atom XML, or YouTube returned an error page | XML ParseError traceback in stderr | Use exact YouTube feed format from Input Types table | Verify URL matches `feeds/videos.xml?channel_id=` or `feeds/videos.xml?playlist_id=` pattern exactly |
| yt-dlp not found | Not installed or not in PATH | `Command not found: yt-dlp` or `FileNotFoundError` | Pre-check: `which yt-dlp` | `brew install yt-dlp` then restart shell; confirm with `yt-dlp --version` |
| Transcript truncated | Video >16K words (~2+ hour video) | `[transcript truncated at 8,000 words]` appears at end of note | Use videos under ~90 minutes for full coverage | Notes still generated; quality may drop for content in the second half of very long videos |
| Network timeout | Slow connection, rate-limited by YouTube, or yt-dlp blocked | `subprocess.TimeoutExpired` or `urllib.error.URLError` | n/a — transient issue | Retry once after 30s; try `yt-dlp --proxy` if consistently blocked in your region |
| Metadata fetch fails | Video is private, age-restricted, or geo-blocked | yt-dlp exits non-zero; metadata returns `{"title": "Unknown", ...}` | n/a | Notes still generated with placeholder metadata; the transcript may also be unavailable |
| Invalid RSS feed | Playlist is empty, private, or channel has no recent videos | Empty `videos` list; script prints "No videos found in RSS feed" | Verify playlist/channel is public and has recent uploads | Try channel RSS instead of playlist RSS; check channel exists at youtube.com |

---

## Self-Healing Additions

When adding a new row, follow this format:

```
| {short error name} | {actual technical root cause} | {exact message or traceback pattern user sees} | {how to avoid it in future} | {step-by-step recovery} |
```

After adding: bump `SKILL.md` metadata.version to next patch (e.g. `2.0.1`).

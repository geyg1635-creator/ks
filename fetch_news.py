import json
import urllib.request
import re
from datetime import datetime

SOURCES = [
    {"name": "百度热搜", "url": "https://api.vvhan.com/api/hotlist/baiduRD"},
    {"name": "今日头条", "url": "https://api.vvhan.com/api/hotlist/toutiao"},
    {"name": "微博热搜", "url": "https://api.vvhan.com/api/hotlist/wbHot"},
]

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"抓取失败: {url} -> {e}")
        return None

def get_history():
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"topics": [], "history": []}

def main():
    history_data = get_history()
    today_news = []

    for src in SOURCES:
        data = fetch(src["url"])
        if not data:
            continue
        items = data.get("data", [])
        if isinstance(items, dict):
            items = items.get("list", [])
        if not isinstance(items, list):
            continue
        for item in items[:6]:
            title = item if isinstance(item, str) else (item.get("title") or item.get("name") or "")
            url = "" if isinstance(item, str) else (item.get("url") or item.get("link") or "")
            if title:
                today_news.append({
                    "title": re.sub(r"<[^>]+>", "", title).strip(),
                    "url": url,
                    "source": src["name"],
                })

    seen = set()
    unique_today = []
    for n in today_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique_today.append(n)

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    today_html = ""
    if unique_today:
        for item in unique_today[:12]:
            link = f'<a href="{item["url"]}" target="_blank">🔗 原文</a>' if item["url"] else ""
            today_html += f'''
            <div class="news-item">
              <div class="title">{item["title"]}</div>
              <div class="meta"><span class="tag">{item["source"]}</span>{link}</div>
            </div>'''
    else:
        today_html = '<div class="empty">今日接口暂无新数据，稍后会自动重试</div>'

    topics_html = ""
    for t in history_data.get("topics", []):
        topics_html += f'''
        <div class="news-item">
          <div class="title">{t["title"]}</div>
          <div class="meta"><span class="tag">{t["tag"]}</span></div>
        </div>'''

    history_html = ""
    for h in history_data.get("history", []):
        history_html += f'''
        <div class="news-item">
          <div class="title">{h["title"]}</div>
          <div class="meta"><span class="tag">{h["tag"]}</span></div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>金融时政 · 每日更新</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, "PingFang SC", "微软雅黑", Arial, sans-serif; background: #eef3fa; min-height: 100vh; padding: 12px; color: #333; font-size: 16px; }}
  .container {{ max-width: 640px; margin: 0 auto; background: #fff; border-radius: 16px; box-shadow: 0 4px 16px rgba(26,58,107,0.1); padding: 18px 16px 24px; }}
  .header {{ text-align: center; margin-bottom: 16px; }}
  .header h1 {{ font-size: 22px; color: #1a3a6b; margin-bottom: 4px; }}
  .header .date {{ font-size: 13px; color: #888; }}
  .section-title {{ font-size: 15px; font-weight: bold; color: #1a3a6b; margin: 20px 0 10px 2px; padding-bottom: 6px; border-bottom: 2px solid #f0f4f8; }}
  .news-item {{ padding: 12px; border-radius: 12px; border: 1.5px solid #eef2f7; background: #fafcff; margin-bottom: 8px; }}
  .news-item .title {{ font-size: 14px; font-weight: 600; color: #2c3e50; line-height: 1.5; margin-bottom: 6px; }}
  .news-item .meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .news-item .tag {{ font-size: 11px; color: #4a90d9; background: #e8f0fe; padding: 2px 8px; border-radius: 6px; }}
  .news-item a {{ font-size: 12px; color: #4a90d9; text-decoration: none; }}
  .empty {{ text-align: center; padding: 20px; color: #999; font-size: 14px; }}
  .footer {{ text-align: center; font-size: 12px; color: #aaa; margin-top: 24px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🏦 金融时政</h1>
    <div class="date">更新于 {updated}</div>
  </div>

  <div class="section-title">📌 今日财经要闻</div>
  {today_html}

  <div class="section-title">💡 银行笔试时政高频考点</div>
  {topics_html}

  <div class="section-title">📚 历史重大金融时政</div>
  {history_html}

  <div class="footer">每天早上 8:00 自动更新</div>
</div>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump({"date": datetime.now().strftime("%Y-%m-%d"), "updated": updated, "news": unique_today}, f, ensure_ascii=False, indent=2)

    print(f"已生成页面，今日新闻 {len(unique_today)} 条")

if __name__ == "__main__":
    main()

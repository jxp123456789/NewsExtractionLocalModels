import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ======================
# 模型
# ======================
OLLAMA_MODEL = "gemma4:latest"  # 这里删掉了多余空格！
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")


# ======================
# 抓取干净新闻
# ======================
def get_news():
    print("🔍 正在获取今日新闻...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 更稳定的新闻源（能抓到完整标题+内容）
    sources = [
        "https://news.sina.com.cn/",
        "https://finance.sina.com.cn/",
        "https://tech.163.com/",
        "https://www.chinanews.com.cn/",
    ]

    articles = []

    for url in sources:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")

            # 抓新闻标题（更干净、AI更好理解）
            for a in soup.find_all("a"):
                title = a.get_text(strip=True)
                if 8 < len(title) < 40 and "广告" not in title and "登录" not in title:
                    articles.append(title)

        except Exception as e:
            continue

    # 去重 + 限制长度
    articles = list(set(articles))[:60]
    return "\n".join(articles)

# ======================
# AI 总结（强制中文 + 正确格式）
# ======================
def summarize(news):
    print("🧠 AI 生成完整新闻简报...")

    # 关键：强制用中文、严格按格式输出
    prompt = f"""
你是专业新闻编辑，必须用**流畅标准的中文**完成任务

请严格按照以下要求生成一份今日新闻简报：

1. 必须分 5 大类：
   - 国内要闻
   - 国际新闻
   - 财经市场
   - 科技动态
   - 社会民生

2. 每类 3～6 条，每条一句话。
3. 内容必须来自下面新闻，不编造、不重复。
4. 必须完整输出，不能中途断掉。
5. 只输出内容，不要解释！

新闻标题如下：
{news}
"""

    response = requests.post("http://localhost:11434/api/generate",
                             json={
                                 "model": OLLAMA_MODEL,
                                 "prompt": prompt,
                                 "stream": False,
                                 "options": {
                                     "temperature": 0.05,
                                     "num_predict": 4096
                                 }
                             })
    return response.json()["response"].strip()

# ======================
# 保存桌面
# ======================
def save(content):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(DESKTOP, f"AI完整新闻简报_{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# AI 完整新闻简报 {today}\n\n")
        f.write(content)
    print(f"✅ 完成！已保存到桌面")


# ======================
# 运行
# ======================
if __name__ == "__main__":
    news = get_news()
    report = summarize(news)
    save(report)
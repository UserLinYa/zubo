import asyncio
import aiohttp
import re
import datetime
import requests
import os
import time
from urllib.parse import urljoin

URL_FILE = "https://raw.githubusercontent.com/kakaxi-1/zubo/main/ip_urls.txt"

CHANNEL_CATEGORIES = {
    "全部频道":
    [
        "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7","CCTV8", "CCTV9",
        "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17", 
        "安徽卫视","北京卫视","东方卫视","东南卫视","广东卫视","广西卫视","贵州卫视","海南卫视","河北卫视","河南卫视",
        "湖北卫视","湖南卫视","吉林卫视","江苏卫视","江西卫视","辽宁卫视","宁夏卫视","青海卫视","山东卫视","山西卫视",
        "陕西卫视","深圳卫视","四川卫视","天津卫视","云南卫视","浙江卫视","重庆卫视","甘肃卫视","西藏卫视","香港卫视",
        "新疆卫视","三沙卫视","兵团卫视","延边卫视","黑龙江卫视","内蒙古卫视"
    ],
}

CHANNEL_MAPPING = {
    "CCTV1":["CCTV-1","CCTV-01","CCTV1-综合","CCTV-1综合","CCTV-1综合","CCTV1HD","CCTV-1高清","CCTV-1HD","cctv-1HD","CCTV1综合高清","cctv1"],
    "CCTV2":["CCTV-2","CCTV-02","CCTV2-财经","CCTV-2财经","CCTV-2财经","CCTV2HD","CCTV-2高清","CCTV-2HD","cctv-2HD","CCTV2财经高清","cctv2"],
    "CCTV3":["CCTV-3","CCTV-03","CCTV3-综艺","CCTV-3综艺","CCTV-3综艺","CCTV3HD","CCTV-3高清","CCTV-3HD","cctv-3HD","CCTV3综艺高清","cctv3"],
    "CCTV4":["CCTV-4","CCTV-04","CCTV4-国际","CCTV-4中文国际","CCTV-4中文国际","CCTV4HD","cctv4HD","CCTV-4HD","CCTV4-中文国际","CCTV4国际高清","cctv4"],
    "CCTV5":["CCTV-5","CCTV-05","CCTV5-体育","CCTV-5体育","CCTV-5体育","CCTV5HD","CCTV-5高清","CCTV-5HD","CCTV5体育","CCTV5体育高清","cctv5"],
    "CCTV5+":["CCTV-5+","CCTV5+体育赛事","CCTV-5+体育赛事","CCTV5+体育赛事","CCTV5+HD","CCTV-5+高清","CCTV-5+HD","cctv-5+HD","CCTV5plas","CCTV5+体育赛视高清","cctv5+"],
    "CCTV6":["CCTV-6","CCTV-06","CCTV6-电影","CCTV-6电影","CCTV-6电影","CCTV6HD","CCTV-6高清","CCTV-6HD","cctv-6HD","CCTV6电影高清","cctv6"],
    "CCTV7":["CCTV-7","CCTV-07","CCTV7-军农","CCTV-7国防军事","CCTV-7国防军事","CCTV7HD","CCTV-7高清","CCTV-7HD","CCTV7-国防军事","CCTV7军事高清","cctv7"],
    "CCTV8":["CCTV-8","CCTV-08","CCTV8-电视剧","CCTV-8电视剧","CCTV-8电视剧","CCTV8HD","CCTV-8高清","CCTV-8HD","cctv-8HD","CCTV8电视剧高清","cctv8"],
    "CCTV9":["CCTV-9","CCTV-09","CCTV9-纪录","CCTV-9纪录","CCTV-9纪录","CCTV9HD","cctv9HD","CCTV-9高清","cctv-9HD","CCTV9记录高清","cctv9"],
    "CCTV10":["CCTV-10","CCTV10-科教","CCTV-10科教","CCTV-10科教","CCTV10HD","CCTV-10高清","CCTV-10HD","CCTV-10高清","CCTV10科教高清","cctv10"],
    "CCTV11":["CCTV-11","CCTV11-戏曲","CCTV-11戏曲","CCTV-11戏曲","CCTV11HD","cctv11HD","CCTV-11HD","cctv-11HD","CCTV11戏曲高清","cctv11"],
    "CCTV12":["CCTV-12","CCTV12-社会与法","CCTV-12社会与法","CCTV-12社会与法","CCTV12HD","CCTV-12高清","CCTV-12HD","cctv-12HD","CCTV12社会与法高清","cctv12"],
    "CCTV13":["CCTV-13","CCTV13-新闻","CCTV-13新闻","CCTV-13新闻","CCTV13HD","cctv13HD","CCTV-13HD","cctv-13HD","CCTV13新闻高清","cctv13"],
    "CCTV14":["CCTV-14","CCTV14-少儿","CCTV-14少儿","CCTV-14少儿","CCTV14HD","CCTV-14高清","CCTV-14HD","CCTV少儿","CCTV14少儿高清","cctv14"],
    "CCTV15":["CCTV-15","CCTV15-音乐","CCTV-15音乐","CCTV-15音乐","CCTV15HD","cctv15HD","CCTV-15HD","cctv-15HD","CCTV15音乐高清","cctv15"],
    "CCTV16":["CCTV-16","CCTV-16HD","CCTV-164K","CCTV-16奥林匹克","CCTV16HD","cctv16HD","CCTV-16HD","cctv-16HD","CCTV16奥林匹克高清","cctv16"],
    "CCTV17":["CCTV-17","CCTV17高清","CCTV17HD","CCTV-17农业农村","CCTV17HD","cctv17HD","CCTV-17HD","cctv-17HD","CCTV17农业农村高清","cctv17"],
}

RESULTS_PER_CHANNEL = 20

def load_urls():
    """从 GitHub 下载 IPTV IP 段列表"""
    import requests
    try:
        resp = requests.get(URL_FILE, timeout=5)
        resp.raise_for_status()
        urls = [line.strip() for line in resp.text.splitlines() if line.strip()]
        print(f"📡 已加载 {len(urls)} 个基础 URL")
        return urls
    except Exception as e:
        print(f"❌ 下载 {URL_FILE} 失败: {e}")
        exit()

async def generate_urls(url):
    modified_urls = []

    ip_start = url.find("//") + 2
    ip_end = url.find(":", ip_start)

    base = url[:ip_start]
    ip_prefix = url[ip_start:ip_end].rsplit('.', 1)[0]
    port = url[ip_end:]

    json_paths = [
    "/iptv/live/1000.json?key=txiptv",
    "/iptv/live/1001.json?key=txiptv",
    "/ZHGXTV/Public/json/live_interface.txt",
]

    for i in range(1, 256):
        ip = f"{base}{ip_prefix}.{i}{port}"
        for path in json_paths:
            modified_urls.append(f"{ip}{path}")

    return modified_urls

async def check_url(session, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url, timeout=1) as resp:#===========================JSON访问时间
                if resp.status == 200:
                    return url
        except:
            return None

async def fetch_json(session, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url, timeout=2) as resp:
                data = await resp.json()
                results = []
                for item in data.get('data', []):
                    name = item.get('name')
                    urlx = item.get('url')
                    if not name or not urlx or ',' in urlx:
                        continue

                    if not urlx.startswith("http"):
                        urlx = urljoin(url, urlx)

                    for std_name, aliases in CHANNEL_MAPPING.items():
                        if name in aliases:
                            name = std_name
                            break

                    results.append((name, urlx))
                return results
        except:
            return []

async def measure_speed(session, url, semaphore):
    async with semaphore:
        start = time.time()
        try:
            async with session.head(url, timeout=2) as resp:  # =======================频道测速用时
                if resp.status == 200:
                    return int((time.time() - start) * 1000)
                else:
                    return 999999
        except:
            return 999999

def is_valid_stream(url):
    if url.startswith(("rtp://", "udp://", "rtsp://")):
        return False
    if "239." in url:
        return False
    if url.startswith(("http://16.", "http://10.", "http://192.168.")):
        return False
    if "/paiptv/" in url or "/00/SNM/" in url or "/00/CHANNEL" in url:
        return False
    valid_ext = (".m3u8", ".ts", ".flv", ".mp4", ".mkv")
    return url.startswith("http") and any(ext in url for ext in valid_ext)

async def main():
    print("🚀 开始运行 ITVlist 脚本")
    semaphore = asyncio.Semaphore(150)  # ==============================================并发限制

    urls = load_urls()
    
    async with aiohttp.ClientSession() as session:
        all_urls = []
        for url in urls:
            modified_urls = await generate_urls(url)
            all_urls.extend(modified_urls)
        print(f"🔍 生成待扫描 URL 共: {len(all_urls)} 个")

        print("⏳ 开始检测可用 JSON API...")
        tasks = [check_url(session, u, semaphore) for u in all_urls]
        valid_urls = [r for r in await asyncio.gather(*tasks) if r]
        print(f"✅ 可用 JSON 地址: {len(valid_urls)} 个")
        for u in valid_urls:
            print(f"  - {u}")

        print("📥 开始抓取节目单 JSON...")
        tasks = [fetch_json(session, u, semaphore) for u in valid_urls]
        results = []
        fetched = await asyncio.gather(*tasks)
        for sublist in fetched:
            results.extend(sublist)
        print(f"📺 抓到频道总数: {len(results)} 条")

        final_results = [(name, url, 0) for name, url in results]

        final_results = [
            (name, url, speed)
            for name, url, speed in final_results
            if is_valid_stream(url)
        ]

        print("🚀 开始测速频道源...")
        speed_tasks = [measure_speed(session, url, semaphore) for (_, url, _) in final_results]
        speeds = await asyncio.gather(*speed_tasks)
        final_results = [
            (name, url, speed)
            for (name, url, _), speed in zip(final_results, speeds)
        ]

        final_results.sort(key=lambda x: x[2])

        itv_dict = {cat: [] for cat in CHANNEL_CATEGORIES}
        for name, url, speed in final_results:
            for cat, channels in CHANNEL_CATEGORIES.items():
                if name in channels:
                    itv_dict[cat].append((name, url, speed))
                    break

        for cat in CHANNEL_CATEGORIES:
            print(f"📦 分类《{cat}》找到 {len(itv_dict[cat])} 条频道")

        beijing_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=8))
        ).strftime("%Y-%m-%d %H:%M:%S")
        disclaimer_url = "https://kakaxi-1.asia/LOGO/Disclaimer.mp4"

        with open("itvlist.txt", 'w', encoding='utf-8') as f:
            f.write(f"更新时间: {beijing_now}（北京时间）\n\n")
            #f.write("更新时间,#genre#\n")
            #f.write(f"{beijing_now},{disclaimer_url}\n\n")

            for cat in CHANNEL_CATEGORIES:
                f.write(f"{cat},#genre#\n")
                for ch in CHANNEL_CATEGORIES[cat]:
                    ch_items = [x for x in itv_dict[cat] if x[0] == ch]
                    ch_items = ch_items[:RESULTS_PER_CHANNEL]
                    for item in ch_items:
                        f.write(f"{item[0]},{item[1]}\n")

        print("🎉 itvlist.txt 已生成完成！")

if __name__ == "__main__":
    asyncio.run(main())

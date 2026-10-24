import asyncio
import datetime
from dataclasses import dataclass, replace
from typing import Optional
from urllib.parse import urljoin

try:  # 允许在没有安装依赖的环境里导入本模块做单元测试
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

URL_FILE = "https://raw.githubusercontent.com/kakaxi-1/zubo/main/ip_urls.txt"

CHANNEL_CATEGORIES = {
    "全部频道":
    [
        "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5","CCTV6", "CCTV7","CCTV8", "CCTV9",
        "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17", 
        "安徽卫视","北京卫视","东方卫视","东南卫视","广东卫视","广西卫视","贵州卫视","海南卫视","河北卫视","河南卫视",
        "湖北卫视","湖南卫视","吉林卫视","江苏卫视","江西卫视","辽宁卫视","宁夏卫视","青海卫视","山东卫视","山西卫视",
        "陕西卫视","深圳卫视","四川卫视","天津卫视","云南卫视","浙江卫视","重庆卫视","甘肃卫视","西藏卫视","香港卫视",
        "新疆卫视","三沙卫视","兵团卫视","延边卫视","黑龙江卫视","内蒙古卫视","大象新闻"
    ],
}

CHANNEL_MAPPING = {
    "CCTV1":["CCTV-1","CCTV-01","CCTV1-综合","CCTV-1综合","CCTV-1综合","CCTV1HD","CCTV-1高清","CCTV-1HD","cctv-1HD","CCTV1综合高清","cctv1"],
    "CCTV2":["CCTV-2","CCTV-02","CCTV2-财经","CCTV-2财经","CCTV-2财经","CCTV2HD","CCTV-2高清","CCTV-2HD","cctv-2HD","CCTV2财经高清","cctv2"],
    "CCTV3":["CCTV-3","CCTV-03","CCTV3-综艺","CCTV-3综艺","CCTV-3综艺","CCTV3HD","CCTV-3高清","CCTV-3HD","cctv-3HD","CCTV3综艺高清","cctv3"],
    "CCTV4":["CCTV-4","CCTV-04","CCTV4-国际","CCTV-4中文国际","CCTV-4中文国际","CCTV4HD","cctv4HD","CCTV-4HD","CCTV4-中文国际","CCTV4国际高清","cctv4"],
    "CCTV5":["CCTV-5","CCTV-05","CCTV5-体育","CCTV-5体育","CCTV-5体育","CCTV5HD","CCTV-5高清","CCTV-5HD","CCTV5体育","CCTV5体育高清","cctv5"],
    #"CCTV5+":["CCTV-5+","CCTV5+体育赛事","CCTV-5+体育赛事","CCTV5+体育赛事","CCTV5+HD","CCTV-5+高清","CCTV-5+HD","cctv-5+HD","CCTV5plas","CCTV5+体育赛视高清","cctv5+"],
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
    "安徽卫视":["安徽卫视高清","安徽卫视4K"],
    "北京卫视":["北京卫视高清","北京卫视4K"],
    "东方卫视":["东方卫视高清","东方卫视4K"],
    "东南卫视":["东南卫视高清","东南卫视4K"],
    "广东卫视":["广东卫视高清","广东卫视4K"],
    "广西卫视":["广西卫视高清","广西卫视4K"],
    "贵州卫视":["贵州卫视高清","贵州卫视4K"],
    "海南卫视":["海南卫视高清","海南卫视4K"],
    "河北卫视":["河北卫视高清","河北卫视4K"],
    "河南卫视":["河南卫视高清","河南卫视4K"],
    "湖北卫视":["湖北卫视高清","湖北卫视4K"],
    "湖南卫视":["湖南卫视高清","湖南卫视4K"],
    "吉林卫视":["吉林卫视高清","吉林卫视4K"],
    "江苏卫视":["江苏卫视高清","江苏卫视4K"],
    "江西卫视":["江西卫视高清","江西卫视4K"],
    "辽宁卫视":["辽宁卫视高清","辽宁卫视4K"],
    "宁夏卫视":["宁夏卫视高清","宁夏卫视4K"],
    "青海卫视":["青海卫视高清","青海卫视4K"],
    "山东卫视":["山东卫视高清","山东卫视4K"],
    "山西卫视":["山西卫视高清","山西卫视4K"],
    "陕西卫视":["陕西卫视高清","陕西卫视4K"],
    "深圳卫视":["深圳卫视高清","深圳卫视4K"],
    "四川卫视":["四川卫视高清","四川卫视4K"],
    "天津卫视":["天津卫视高清","天津卫视4K"],
    "云南卫视":["云南卫视高清","云南卫视4K"],
    "浙江卫视":["浙江卫视高清","浙江卫视4K"],
    "重庆卫视":["重庆卫视高清","重庆卫视4K"],
    "甘肃卫视":["甘肃卫视高清","甘肃卫视4K"],
    "西藏卫视":["西藏卫视高清","西藏卫视4K"],
    "香港卫视":["香港卫视高清","香港卫视4K"],
    "新疆卫视":["新疆卫视高清","新疆卫视4K"],
    "三沙卫视":["三沙卫视高清","三沙卫视4K"],
    "兵团卫视":["兵团卫视高清","兵团卫视4K"],
    "延边卫视":["延边卫视高清","延边卫视4K"],
    "黑龙江卫视":["黑龙江卫视高清","黑龙江卫视4K"],
    "内蒙古卫视":["内蒙古卫视高清","内蒙古卫视4K"],
}

RESULTS_PER_CHANNEL = 20

# ==================== 播放源测速排序配置 ====================
SPEED_TEST_ENABLED = True        # 关闭后按抓取到的原始顺序输出（不测速）
SPEED_CONCURRENCY = 48           # 同时测速的源数量
SPEED_SAMPLE_BYTES = 320 * 1024  # 每个源最多采样多少字节
SPEED_MIN_SAMPLE_BYTES = 24 * 1024  # 采样量达到该值才认为“实测速度”有效
SPEED_TIMEOUT = 5.0              # 单个 HTTP 请求（连接+读取）最长耗时
SPEED_CONNECT_TIMEOUT = 3.0      # 建立连接超时
SPEED_MAX_SECONDS = 14.0         # 单个源（含 m3u8 多级跳转、重试）总耗时上限
SPEED_RETRIES = 1                # 失败重试次数（仅网络类错误重试）
SPEED_TLS_VERIFY = False         # 部分源证书不规范，关闭校验以兼容
SPEED_REPORT_FILE = "speed_report.txt"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    # 只取开头一段，避免把点播大文件整个拖下来
    "Range": f"bytes=0-{SPEED_SAMPLE_BYTES - 1}",
}


def load_urls():
    """从 GitHub 下载 IPTV IP 段列表"""
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
            async with session.get(url, timeout=1) as resp:  # JSON访问时间
                if resp.status == 200:
                    return url
        except Exception:
            return None
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
        except Exception:
            return []


@dataclass
class ProbeResult:
    """单个播放源的测速结果。"""
    name: str
    url: str
    ok: bool = False
    kbps: Optional[float] = None      # 实测下载速度（千比特/秒），None 表示只验证了可访问
    latency_ms: float = 999999.0      # 首字节耗时（毫秒）
    sample_bytes: int = 0             # 实际采样字节数
    seconds: float = 0.0              # 采样耗时（秒）
    via: str = ""                     # direct / hls
    error: str = ""

    @property
    def tier(self) -> int:
        """排序优先级：0=有实测速度，1=仅可访问，2=不可用。"""
        if not self.ok:
            return 2
        return 0 if self.kbps is not None else 1


@dataclass
class _Sample:
    """一次 HTTP 采样的原始结果。"""
    status: int = 0
    content_type: str = ""
    final_url: str = ""
    data: bytes = b""
    first_at: Optional[float] = None
    last_at: float = 0.0
    start: float = 0.0
    error: str = ""


def _rank_key(item: ProbeResult):
    """同一频道内的排序：先按实测速度从快到慢，再按首字节延迟从低到高。"""
    speed = -item.kbps if item.kbps is not None else 0.0
    return (item.tier, speed, item.latency_ms)


def dedupe_sources(pairs):
    """按 (频道, 地址) 去重，保持首次出现的顺序。"""
    seen = set()
    unique = []
    for name, url in pairs:
        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, url))
    return unique


def group_names_by_url(pairs):
    """把同一地址的多个频道名归并，保证一个地址只测速一次。"""
    url_names = {}
    for name, url in pairs:
        names = url_names.setdefault(url, [])
        if name not in names:
            names.append(name)
    return url_names


def rank_channel_sources(results, keep=RESULTS_PER_CHANNEL):
    """按频道分组并按速度排序，只保留可访问源，每个频道最多 keep 条。

    返回 {频道名: [ProbeResult, ...]}，列表第一个就是该频道最快的源。
    """
    grouped = {}
    for item in results:
        grouped.setdefault(item.name, []).append(item)

    ranked = {}
    for name, items in grouped.items():
        seen = set()
        picked = []
        for item in sorted(items, key=_rank_key):
            if not item.ok or item.url in seen:
                continue
            seen.add(item.url)
            picked.append(item)
            if len(picked) >= keep:
                break
        if picked:
            ranked[name] = picked
    return ranked


def parse_playlist(content):
    """解析 m3u8：返回 ("variant"|"segment", 地址) 或 None。"""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return None

    if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
        for index, line in enumerate(lines):
            if not line.startswith("#EXT-X-STREAM-INF"):
                continue
            for following in lines[index + 1:]:
                if not following.startswith("#"):
                    return ("variant", following)
        return None

    for line in lines:
        if not line.startswith("#"):
            return ("segment", line)
    return None


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


def _is_playlist(sample: "_Sample") -> bool:
    content_type = (sample.content_type or "").lower()
    if "mpegurl" in content_type:
        return True
    return sample.data.lstrip()[:7].upper().startswith(b"#EXTM3U")


def _build_media_result(name, url, sample, via):
    """把媒体采样数据换算成速度结果。"""
    if sample.error:
        return ProbeResult(name, url, error=sample.error)

    size = len(sample.data)
    if size == 0:
        return ProbeResult(name, url, error="空响应")

    first_at = sample.first_at if sample.first_at is not None else sample.last_at
    latency_ms = max((first_at - sample.start) * 1000.0, 0.0)
    duration = max(sample.last_at - first_at, 0.001)
    kbps = None
    if size >= SPEED_MIN_SAMPLE_BYTES:
        kbps = min(size * 8 / 1000.0 / duration, 500000.0)  # 上限 500 Mbps，规避计时误差

    return ProbeResult(
        name=name,
        url=url,
        ok=True,
        kbps=kbps,
        latency_ms=round(latency_ms, 1),
        sample_bytes=size,
        seconds=round(duration, 3),
        via=via,
    )


async def _get_sample(session, url, timeout_s):
    """读取 url 开头最多 SPEED_SAMPLE_BYTES 字节，超时也保留已收到的部分。"""
    loop = asyncio.get_running_loop()
    start = loop.time()
    data = bytearray()
    first_at = None
    last_at = start
    status = 0
    content_type = ""
    final_url = url

    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s, connect=SPEED_CONNECT_TIMEOUT)
        async with session.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        ) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            final_url = str(resp.url)
            if status not in (200, 206):
                return _Sample(
                    status=status,
                    content_type=content_type,
                    final_url=final_url,
                    start=start,
                    last_at=start,
                    error=f"HTTP {status}",
                )

            async for chunk in resp.content.iter_chunked(64 * 1024):
                now = loop.time()
                if first_at is None:
                    first_at = now
                data.extend(chunk)
                last_at = now
                if len(data) >= SPEED_SAMPLE_BYTES or (now - start) >= timeout_s:
                    break
    except asyncio.TimeoutError:
        if not data:
            return _Sample(status=status, content_type=content_type, final_url=final_url,
                           start=start, last_at=start, error="连接超时")
    except Exception as exc:  # 网络错误、SSL 错误、协议错误等
        if not data:
            return _Sample(status=status, content_type=content_type, final_url=final_url,
                           start=start, last_at=start,
                           error=f"{type(exc).__name__}: {exc}")

    return _Sample(
        status=status,
        content_type=content_type,
        final_url=final_url,
        data=bytes(data),
        first_at=first_at,
        last_at=last_at,
        start=start,
    )


async def _probe_url(session, name, url, depth=0):
    """探测一个地址：直连流直接测速；m3u8 则解析出首个分片后再测速。"""
    if depth > 2:
        return ProbeResult(name, url, error="播放列表层级过深")

    sample = await _get_sample(session, url, SPEED_TIMEOUT)
    if sample.error:
        return ProbeResult(name, url, error=sample.error)

    if not _is_playlist(sample):
        return _build_media_result(name, url, sample, "direct")

    text = sample.data.decode("utf-8", "replace")
    parsed = parse_playlist(text)
    if parsed is None:
        return ProbeResult(name, url, error="无法解析播放列表")

    kind, reference = parsed
    target = urljoin(sample.final_url, reference)

    if kind == "variant":
        # 主播放列表（多码率）→ 继续解析子播放列表
        sub = await _probe_url(session, name, target, depth + 1)
    else:
        # 媒体播放列表 → 直接测第一个分片
        sub_sample = await _get_sample(session, target, SPEED_TIMEOUT)
        sub = _build_media_result(name, url, sub_sample, "hls")

    if not sub.ok:
        return ProbeResult(name, url, error=sub.error or "分片不可用")

    manifest_ttfb = (sample.first_at - sample.start) * 1000.0 if sample.first_at else 0.0
    return ProbeResult(
        name=name,
        url=url,
        ok=True,
        kbps=sub.kbps,
        latency_ms=round(sub.latency_ms + manifest_ttfb, 1),
        sample_bytes=sub.sample_bytes,
        seconds=sub.seconds,
        via="hls",
    )


async def probe_source(session, name, url, semaphore):
    """带并发限制、超时与重试的单源测速入口。"""
    async with semaphore:
        result = ProbeResult(name, url)
        for attempt in range(SPEED_RETRIES + 1):
            try:
                result = await asyncio.wait_for(
                    _probe_url(session, name, url),
                    timeout=SPEED_MAX_SECONDS,
                )
            except asyncio.TimeoutError:
                result = ProbeResult(name, url, error="测速超时")
            except Exception as exc:
                result = ProbeResult(name, url, error=f"{type(exc).__name__}: {exc}")

            if result.ok or result.error.startswith("HTTP "):
                return result
            if attempt < SPEED_RETRIES:
                await asyncio.sleep(0.3)
        return result


def _ordered_channel_names(ranked):
    """按 CHANNEL_CATEGORIES 定义的顺序列出频道，未定义的频道排最后。"""
    ordered = []
    for channels in CHANNEL_CATEGORIES.values():
        for channel in channels:
            if channel in ranked and channel not in ordered:
                ordered.append(channel)
    for channel in ranked:
        if channel not in ordered:
            ordered.append(channel)
    return ordered


def print_channel_leaders(ranked):
    """打印每个频道排名第一的源，便于在 Actions 日志里核对。"""
    print("🏆 各频道最快播放源（同频道内已按速度排序）:")
    for name in _ordered_channel_names(ranked):
        best = ranked[name][0]
        if best.kbps is not None:
            speed = f"{best.kbps / 1000:.2f} Mbps"
        else:
            speed = f"仅响应 {best.latency_ms:.0f} ms"
        print(f"  {name}: {speed} | {best.url}")


def write_speed_report(ranked, generated_at, path=SPEED_REPORT_FILE):
    """输出完整测速报告，itvlist.txt 只写地址，报告里保留速度数据。"""
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 频道播放源测速排序报告（每个频道按实测速度从快到慢）\n")
        f.write(f"# 生成时间: {generated_at}（北京时间）\n")
        f.write("# 频道\t排名\t速度(kbps)\t延迟(ms)\t采样(bytes)\t方式\t地址\n")
        for name in _ordered_channel_names(ranked):
            for index, item in enumerate(ranked[name], 1):
                speed = f"{item.kbps:.1f}" if item.kbps is not None else "-"
                f.write(
                    f"{name}\t{index}\t{speed}\t{item.latency_ms:.0f}\t"
                    f"{item.sample_bytes}\t{item.via}\t{item.url}\n"
                )


def write_itvlist(channel_urls, beijing_now, disclaimer_url, path="itvlist.txt"):
    """按分类/频道输出 itvlist.txt，每个频道内最快的源排在最前面。"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"更新时间: {beijing_now}（北京时间）\n\n")
        # f.write("更新时间,#genre#\n")
        # f.write(f"{beijing_now},{disclaimer_url}\n\n")

        for cat in CHANNEL_CATEGORIES:
            f.write(f"{cat},#genre#\n")
            for channel in CHANNEL_CATEGORIES[cat]:
                for url in channel_urls.get(channel, [])[:RESULTS_PER_CHANNEL]:
                    f.write(f"{channel},{url}\n")
        f.write("更新时间,#genre#\n\n")
        f.write(f"{beijing_now},{disclaimer_url}\n\n")


async def main():
    if aiohttp is None:
        raise SystemExit("缺少依赖 aiohttp，请先执行: pip install aiohttp requests")
    print("🚀 开始运行 ITVlist 脚本")
    semaphore = asyncio.Semaphore(150)  # ==============================================并发限制

    urls = load_urls()

    connector = aiohttp.TCPConnector(
        limit=256,
        limit_per_host=8,
        ttl_dns_cache=300,
        ssl=False if not SPEED_TLS_VERIFY else None,
    )
    async with aiohttp.ClientSession(
        connector=connector, headers={"User-Agent": USER_AGENT}
    ) as session:
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

        pairs = dedupe_sources(
            [(name, url) for name, url in results if is_valid_stream(url)]
        )
        print(f"🧹 去重后有效播放源: {len(pairs)} 条")

        beijing_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=8))
        ).strftime("%y/%m/%d-%H:%M:%S")

        if SPEED_TEST_ENABLED:
            url_names = group_names_by_url(pairs)
            print(f"🚀 开始测速 {len(url_names)} 个播放源（同一地址只测一次）...")
            speed_semaphore = asyncio.Semaphore(SPEED_CONCURRENCY)
            probed = await asyncio.gather(
                *(
                    probe_source(session, names[0], url, speed_semaphore)
                    for url, names in url_names.items()
                )
            )

            probes = []
            for (_, names), base in zip(url_names.items(), probed):
                for name in names:
                    probes.append(replace(base, name=name))

            reachable = sum(1 for item in probes if item.ok)
            print(f"✅ 测速完成: 可播放 {reachable}/{len(probes)} 条")

            ranked = rank_channel_sources(probes, keep=RESULTS_PER_CHANNEL)
            print_channel_leaders(ranked)
            write_speed_report(ranked, beijing_now)
            print(f"📄 测速报告已写入: {SPEED_REPORT_FILE}")
        else:
            print("⚠️ 已关闭测速，按抓取顺序输出")
            ranked = {}
            for name, url in pairs:
                bucket = ranked.setdefault(name, [])
                if len(bucket) < RESULTS_PER_CHANNEL:
                    bucket.append(ProbeResult(name=name, url=url, ok=True, latency_ms=0.0))

        channel_urls = {
            name: [item.url for item in items] for name, items in ranked.items()
        }

        for cat in CHANNEL_CATEGORIES:
            count = sum(
                1
                for channel in CHANNEL_CATEGORIES[cat]
                for _ in channel_urls.get(channel, [])[:RESULTS_PER_CHANNEL]
            )
            print(f"📦 分类《{cat}》输出 {count} 条")

        disclaimer_url = "http://kakaxi.indevs.in/LOGO/Disclaimer.mp4"
        write_itvlist(channel_urls, beijing_now, disclaimer_url)
        print("🎉 itvlist.txt 已生成完成！")


if __name__ == "__main__":
    asyncio.run(main())

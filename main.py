import http.client
import json
import os
import requests
import time
from tqdm import tqdm
import re

# 設定檔案路徑
CONFIG_FILE = "config.json"

# 預設下載資料夾
DEFAULT_DOWNLOAD_FOLDER = os.path.expandvars(r"%LOCALAPPDATA%\osu!\Songs")

def load_config():
    """載入設定檔"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"download_folder": DEFAULT_DOWNLOAD_FOLDER}
    return {"download_folder": DEFAULT_DOWNLOAD_FOLDER}

def save_config(config):
    """儲存設定檔"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def set_download_folder():
    """設定下載資料夾"""
    config = load_config()
    current_folder = config.get("download_folder", DEFAULT_DOWNLOAD_FOLDER)
    
    print(f"\n目前的下載資料夾: {current_folder}")
    new_folder = input("請輸入新的下載資料夾路徑 (直接按Enter保持不變): ").strip()
    
    if new_folder:
        try:
            os.makedirs(new_folder, exist_ok=True)
            config["download_folder"] = new_folder
            save_config(config)
            print(f"下載資料夾已更新為: {new_folder}")
            return new_folder
        except Exception as e:
            print(f"設定資料夾失敗: {e}")
            return current_folder
    return current_folder

def search_beatmaps(query=None, limit=10000, offset=0, status=None, mode=None, sort=None):
    """搜尋 beatmap"""
    conn = http.client.HTTPSConnection("catboy.best")
    path = "/api/v2/search"

    params = []
    if query:
        params.append(f"query={query}")
    if limit != 100:
        params.append(f"limit={limit}")
    if offset > 0:
        params.append(f"offset={offset}")
    if status:
        params.append(f"status={','.join(map(str, status))}")
    if mode:
        params.append(f"mode={','.join(map(str, mode))}")
    if sort:
        params.append(f"sort={','.join(map(str, sort))}")
    
    if params:
        path += "?" + "&".join(params)

    print(f"Requesting: https://catboy.best{path}")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    if res.status == 200:
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"JSON 解碼錯誤: {e}")
            print(f"原始資料: {data.decode('utf-8')}")
            return None
    else:
        print(f"API 失敗: {res.status}")
        print(f"內容: {data.decode('utf-8')}")
        return None

def sanitize_filename(filename):
    """移除非法檔名字元"""
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    if len(sanitized) > 250:
        name_part, ext_part = os.path.splitext(sanitized)
        sanitized = name_part[:250-len(ext_part)] + ext_part
    return sanitized

def download_beatmap(beatmap_set_id, beatmap_title, download_folder=None):
    """下載 beatmap"""
    fallback_urls = [
        f"https://catboy.best/d/{beatmap_set_id}",
        f"https://nerinyan.moe/d/{beatmap_set_id}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    raw_filename = f"{beatmap_set_id} {beatmap_title}.osz"
    safe_filename = sanitize_filename(raw_filename)
    folder = download_folder if download_folder else DEFAULT_DOWNLOAD_FOLDER
    filename = os.path.join(folder, safe_filename)

    for url in fallback_urls:
        print(f"\n嘗試下載: {beatmap_title} (ID: {beatmap_set_id})\n來源: {url}")
        for attempt in range(3):
            try:
                response = requests.get(url, stream=True, headers=headers, timeout=30)
                if response.status_code == 425:
                    print("⚠️ 425 Too Early，等待 5 秒重試...")
                    time.sleep(5)
                    continue
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                with open(filename, 'wb') as file, tqdm(
                    desc=beatmap_title,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        pbar.update(size)

                print(f"✅ 下載完成: {filename}")
                return True
            except requests.RequestException as e:
                print(f"❌ 第 {attempt+1} 次嘗試失敗: {e}")
                time.sleep(2)

        print(f"⚠️ 來源 {url} 全部失敗，換下一個...")

    print(f"❌ 無法下載: {beatmap_title} (ID: {beatmap_set_id})")
    return False

def main():
    global DOWNLOAD_FOLDER
    DOWNLOAD_FOLDER = set_download_folder()

    print("\n請輸入搜尋參數（直接 Enter 使用預設）：")
    query = input("關鍵字 (預設: 最新): ").strip() or None
    limit = input("數量限制 (預設: 100): ").strip()
    limit = int(limit) if limit.isdigit() else 100
    offset = input("偏移量 (預設: 0): ").strip()
    offset = int(offset) if offset.isdigit() else 0

    status_input = input("狀態過濾 (例如 2 表示 Ranked，逗號分隔): ").strip()
    status = [int(s.strip()) for s in status_input.split(',')] if status_input else None

    mode_input = input("模式過濾 (例如 3 表示 Mania，逗號分隔): ").strip()
    mode = [int(m.strip()) for m in mode_input.split(',')] if mode_input else None

    sort_input = input("排序方式 (例如: ranked_desc): ").strip()
    sort = sort_input.split(',') if sort_input else None

    search_results = search_beatmaps(query=query, limit=limit, offset=offset,
                                     status=status, mode=mode, sort=sort)
    
    if search_results:
        if isinstance(search_results, list):
            beatmaps_list = search_results
        elif isinstance(search_results, dict):
            beatmaps_list = search_results.get('results', search_results.get('beatmaps', []))
        else:
            print("⚠️ 無法解析回應格式")
            return

        print(f"🔍 找到 {len(beatmaps_list)} 張圖譜")

        for beatmap_info in beatmaps_list:
            beatmap_id = beatmap_info.get('id')
            beatmapset_id = beatmap_info.get('beatmapset_id', beatmap_info.get('id'))
            title = beatmap_info.get('title', 'Unknown Title')
            artist = beatmap_info.get('artist', 'Unknown Artist')

            print(f"\n🎵 {title} - {artist} (ID: {beatmap_id}, SetID: {beatmapset_id})")

            if beatmapset_id:
                download_beatmap(beatmapset_id, f"{artist} - {title}")
            else:
                print(f"⚠️ 缺少 beatmapset_id，無法下載")
    else:
        print("❌ 搜尋失敗或無結果")

if __name__ == "__main__":
    main()

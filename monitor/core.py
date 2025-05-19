import os
import httpx
import psutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def format_bytes(size_in_bytes: int) -> str:
    """Convert bytes to megabytes with one decimal."""
    return f"{size_in_bytes / (1024 ** 2):.1f} MB"


def get_system_info() -> str:
    """Gather general system stats: RAM and CPU."""
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)

    info = (
        "📊  Server holati:\n"  # noqa
        f"💾 Umumiy RAM: {format_bytes(memory.total)}\n"  # noqa
        f"📉 RAM Bo'sh:  {format_bytes(memory.available)} ({100 - memory.percent:.1f}% bo‘sh)\n"  # noqa
        f"🧠 RAM Foydalanilgan: {memory.percent:.1f}%\n"  # noqa
        f"🧮 CPU Yuklama: {cpu}%\n\n"  # noqa
    )
    return info


def get_system_services_report() -> str:
    """Report on running system-level services (from /home/ paths)."""
    services = []

    for proc in psutil.process_iter([
        'pid', 'username', 'cpu_percent', 'memory_percent',
        'memory_info', 'create_time', 'cmdline', 'name', 'status'
    ]):
        try:
            info = proc.info
            cmd = " ".join(info['cmdline']) if info['cmdline'] else info.get('name', "N/A")
            if not cmd.startswith("/home/"):
                continue

            service = {
                'pid': info['pid'],
                'user': info['username'],
                'cpu': info['cpu_percent'],
                'mem_percent': info['memory_percent'],
                'mem_usage': info['memory_info'].rss,
                'start_time': datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S"),
                'cmd': cmd,
                'status': info['status'].upper(),
            }
            services.append(service)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not services:
        return "🔒 Hech qanday system servis topilmadi."  # noqa

    report = "🔒 Ishlayotgan system servislar (/home/...):\n\n"  # noqa
    for s in services:
        report += (
            f"PID: `{s['pid']}` | USER: `{s['user']}`\n"
            f"STATUS: {s['status']}\n"
            f"CPU: {s['cpu']}%, MEM: {s['mem_percent']:.1f}% ({format_bytes(s['mem_usage'])})\n"
            f"STARTED: `{s['start_time']}`\n"
            f"CMD: `{s['cmd']}`\n\n"
        )
    return report


def get_full_system_report() -> str:
    """Full system status and running /home-based service overview."""
    return get_system_info() + get_system_services_report()


def send_report_to_telegram():
    token = os.getenv("BOT_TOKEN")
    topic_id = os.getenv("TOPIC_CHAT_ID")
    message_thread_id = 105  # Message thread ID (topic)

    if not token or not topic_id:
        print("❌ Bot token yoki chat ID topilmadi.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": topic_id,
        "message_thread_id": message_thread_id,
        "text": get_full_system_report(),
        "parse_mode": "Markdown",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)

        if response.status_code != 200:
            print(f"❌ Xatolik: {response.status_code} - {response.text}")  # noqa
        else:
            print("✅ Hisobot yuborildi.")  # noqa
    except httpx.RequestError as e:
        print(f"🔌 HTTP xatolik: {e}")  # noqa


if __name__ == "__main__":
    print(send_report_to_telegram())
    print(get_full_system_report())

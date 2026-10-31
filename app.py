import os
import sys
import time
import queue
import shutil
import tempfile
import threading
import traceback
from multiprocessing import freeze_support

import webview

WINDOW_TITLE = "SamCalculator"

# Размеры окна: (режим, научный) -> (ширина, высота)
WINDOW_SIZES = {
    ("vertical", False): (400, 700),
    ("vertical", True): (400, 740),
    ("horizontal", False): (760, 554),
    ("horizontal", True): (900, 554),
}


# ---------------------------------------------------------------- вспомогательное
def resource_path(name):
    """Путь к файлу и при обычном запуске, и внутри собранного exe (--onedir)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def log_dir():
    """Куда писать журналы: рядом с exe (или с app.py)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _write_log(filename, text):
    for folder in (log_dir(), tempfile.gettempdir()):
        try:
            with open(os.path.join(folder, filename), "a", encoding="utf-8") as f:
                f.write(text + "\n")
            return
        except Exception:
            continue


def log_error(text):
    """Ошибки: calculator_error.log рядом с exe."""
    _write_log("calculator_error.log", text)


def trace(text):
    """Короткий журнал запуска и операций с окном: calculator_debug.log.

    Если программа когда-нибудь зависнет, по последней строке видно, на какой
    операции это случилось. Файл можно прислать для разбора."""
    _write_log("calculator_debug.log", "%s  %s" % (time.strftime("%H:%M:%S"), text))


def reset_debug_log():
    """Не даёт журналу расти бесконечно: при старте начинаем заново, если он большой."""
    path = os.path.join(log_dir(), "calculator_debug.log")
    try:
        if os.path.exists(path) and os.path.getsize(path) > 100 * 1024:
            os.remove(path)
    except Exception:
        pass


def show_message(text):
    """Показывает окно с сообщением (Windows), если программа не смогла запуститься."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, WINDOW_TITLE, 0x10)
    except Exception:
        pass


# ---------------------------------------------------------------- файлы данных
_FILE_LOCK = threading.Lock()


def data_path(name):
    """Файлы с данными (настройки, история) лежат в %APPDATA%\\SamCalculator."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "SamCalculator", name)


def read_text(name):
    with _FILE_LOCK:
        try:
            with open(data_path(name), "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""


def write_text(name, data, limit):
    """Запись целиком и атомарно: сначала во временный файл, потом подмена.

    Так файл не может остаться наполовину записанным, даже если программу
    закроют в момент сохранения. Записи идут строго по одной."""
    if not isinstance(data, str) or len(data) > limit:
        return False
    with _FILE_LOCK:
        try:
            path = data_path(name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(data)
            os.replace(tmp, path)
            return True
        except Exception:
            log_error(traceback.format_exc())
            return False


# ---------------------------------------------------------------- Windows: окно и иконка
# Всё ниже работает напрямую через user32, свои копии функций (WinDLL), чтобы не
# трогать настройки, которые использует сама pywebview. Ни один вызов не может
# повесить программу: закрепление идёт асинхронно, иконка с тайм-аутом.
class Win32:
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.wintypes = wintypes
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        u.FindWindowW.restype = wintypes.HWND
        u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, wintypes.UINT]
        u.SetWindowPos.restype = wintypes.BOOL
        u.GetSystemMetrics.argtypes = [ctypes.c_int]
        u.GetSystemMetrics.restype = ctypes.c_int
        u.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                 ctypes.c_int, ctypes.c_int, wintypes.UINT]
        u.LoadImageW.restype = wintypes.HANDLE
        u.SendMessageTimeoutW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM,
                                          wintypes.LPARAM, wintypes.UINT, wintypes.UINT,
                                          ctypes.POINTER(ctypes.c_size_t)]
        u.SendMessageTimeoutW.restype = ctypes.c_ssize_t
        self.u = u

    def find_window(self, tries=30):
        for _ in range(tries):
            hwnd = self.u.FindWindowW(None, WINDOW_TITLE)
            if hwnd:
                return hwnd
            time.sleep(0.1)
        return None

    def set_topmost(self, flag):
        hwnd = self.find_window()
        if not hwnd:
            return False
        after = self.wintypes.HWND(-1 if flag else -2)  # HWND_TOPMOST / HWND_NOTOPMOST
        # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS
        return bool(self.u.SetWindowPos(hwnd, after, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x4000))

    def set_icon(self, path):
        hwnd = self.find_window()
        if not hwnd:
            return False
        u = self.u
        done = False
        for kind, cx, cy in ((1, 11, 12), (0, 49, 50)):  # ICON_BIG / ICON_SMALL
            handle = u.LoadImageW(None, path, 1, u.GetSystemMetrics(cx), u.GetSystemMetrics(cy), 0x10)
            if handle:
                result = self.ctypes.c_size_t(0)
                # WM_SETICON, SMTO_ABORTIFHUNG, ждём не дольше 2 секунд
                u.SendMessageTimeoutW(hwnd, 0x0080, kind, handle, 0x0002, 2000, self.ctypes.byref(result))
                done = True
        return done


def get_win32():
    if sys.platform != "win32":
        return None
    try:
        return Win32()
    except Exception:
        log_error(traceback.format_exc())
        return None


# ---------------------------------------------------------------- API для страницы
class CalculatorAPI:
    def __init__(self):
        # ВАЖНО: имена с подчёркиванием. pywebview обходит все «открытые» атрибуты
        # этого объекта, чтобы отдать их в JavaScript. Если там лежит само окно,
        # замок или очередь, он начинает обходить и их. Атрибуты с «_» он пропускает.
        self._window = None
        self._ready = threading.Event()
        self._ready_at = None
        self._jobs = queue.Queue()
        self._size_key = ("vertical", False)   # окно создаётся именно таким
        self._topmost = False
        self._win32 = None
        threading.Thread(target=self._worker, daemon=True).start()

    # --- очередь операций с окном -------------------------------------------------
    # Причина прежних зависаний: размер окна и «поверх всех окон» запрашивались
    # из потока страницы в тот самый момент, пока окно ещё поднималось. Теперь все
    # такие операции стоят в одной очереди, идут по одной и стартуют только когда
    # страница сообщила, что загрузилась (плюс короткая пауза).
    def _worker(self):
        self._ready.wait(8.0)
        while True:
            fn, args = self._jobs.get()
            if self._ready_at is not None:
                pause = self._ready_at + 0.7 - time.monotonic()
                if pause > 0:
                    time.sleep(pause)
            try:
                fn(*args)
            except Exception:
                log_error(traceback.format_exc())

    def _enqueue(self, fn, *args):
        self._jobs.put((fn, args))

    def start_icon(self):
        """Ставит иконку favicon.ico окну (и панели задач) после запуска."""
        path = resource_path("favicon.ico")
        if os.path.exists(path):
            self._enqueue(self._do_icon, path)
        else:
            trace("icon: favicon.ico not found")

    def _w32(self):
        if self._win32 is None:
            self._win32 = get_win32()
        return self._win32

    def _do_icon(self, path):
        w32 = self._w32()
        trace("icon: start")
        ok = bool(w32 and w32.set_icon(path))
        trace("icon: done ok=%s" % ok)

    def _do_resize(self, width, height):
        trace("resize: start %sx%s" % (width, height))
        self._window.resize(width, height)
        trace("resize: done")

    def _do_topmost(self, flag):
        trace("topmost: start %s" % flag)
        w32 = self._w32()
        ok = bool(w32 and w32.set_topmost(flag))
        trace("topmost: done ok=%s" % ok)

    # --- вызывается со страницы ---------------------------------------------------
    def notify_ready(self):
        """Страница сообщает, что загрузилась и можно трогать окно."""
        if not self._ready.is_set():
            self._ready_at = time.monotonic()
            self._ready.set()
            trace("page ready")
        return True

    def set_window_size(self, mode, sci=False):
        if self._window is None:
            return False
        key = ("horizontal" if mode == "horizontal" else "vertical", bool(sci))
        if key == self._size_key:
            return True          # окно уже такого размера, ничего не делаем
        self._size_key = key
        width, height = WINDOW_SIZES[key]
        self._enqueue(self._do_resize, width, height)
        return True

    def set_on_top(self, flag):
        """Закрепляет окно поверх остальных (или снимает закрепление)."""
        flag = bool(flag)
        if flag == self._topmost:
            return True
        self._topmost = flag
        self._enqueue(self._do_topmost, flag)
        return True

    def load_settings(self):
        """Отдаёт сохранённые настройки (строка JSON) или пустую строку."""
        return read_text("settings.json")

    def save_settings(self, data):
        """Сохраняет настройки, которые прислала страница."""
        return write_text("settings.json", data, 12 * 1024 * 1024)

    def load_history(self):
        """Отдаёт сохранённую историю расчётов (строка JSON) или пустую строку."""
        return read_text("history.json")

    def save_history(self, data):
        """Сохраняет историю расчётов вместе с заметками."""
        return write_text("history.json", data, 2 * 1024 * 1024)


# ---------------------------------------------------------------- запуск
def main():
    reset_debug_log()
    trace("start")
    html_path = resource_path("samcalculator.html")
    if not os.path.exists(html_path):
        message = (
            "Не найден файл samcalculator.html.\n\n"
            "Соберите exe с параметром:\n"
            '--add-data "samcalculator.html;."'
        )
        log_error(message)
        show_message(message)
        return

    # Для каждого запуска отдельная временная папка браузерного движка.
    # Если прошлый запуск закрылся некорректно и оставил свою папку «занятой»,
    # новый запуск не будет об неё спотыкаться и зависать.
    storage = tempfile.mkdtemp(prefix="samgcalc_")

    try:
        api = CalculatorAPI()
        width, height = WINDOW_SIZES[("vertical", False)]
        window = webview.create_window(
            WINDOW_TITLE,
            html_path,
            js_api=api,
            width=width,
            height=height,
            resizable=True,
            min_size=(320, 450),
        )
        api._window = window
        api.start_icon()
        trace("webview.start")
        webview.start(debug=False, storage_path=storage)
        trace("closed normally")
    except Exception:
        err = traceback.format_exc()
        log_error(err)
        trace("crash, see calculator_error.log")
        show_message("Калькулятор не смог запуститься.\n\nПодробности в файле calculator_error.log")
    finally:
        shutil.rmtree(storage, ignore_errors=True)


if __name__ == "__main__":
    freeze_support()
    main()

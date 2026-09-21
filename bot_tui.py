import os
import sys
import json
import time
import random
import pandas as pd
from dotenv import load_dotenv, set_key

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, Label, ProgressBar, RichLog, Switch
)
from textual.binding import Binding
from textual import work
from label_studio_sdk.client import LabelStudio

# Load environment variables
ENV_PATH = ".env"
load_dotenv(ENV_PATH)


class StatCard(Static):
    """Widget card untuk menampilkan angka statistik."""
    def __init__(self, title: str, value: str = "0", id: str | None = None, classes: str | None = None):
        super().__init__(id=id, classes=classes)
        self.title_text = title
        self.value_text = value

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="stat-title")
        yield Label(self.value_text, id=f"{self.id}-value", classes="stat-value")

    def update_value(self, new_value: str):
        self.value_text = str(new_value)
        try:
            val_widget = self.query_one(f"#{self.id}-value", Label)
            val_widget.update(str(new_value))
        except Exception:
            pass


class ActiveTaskCard(Static):
    """Widget card untuk rincian task yang sedang aktif diproses."""
    def compose(self) -> ComposeResult:
        yield Label("📋 TASK SAAT INI", classes="card-header")
        yield Static("Belum ada task yang diproses", id="active-task-info", classes="active-info")

    def update_info(self, excel_id: str = "-", internal_id: str = "-", label_val: str = "-", status: str = "-"):
        info_text = (
            f"[bold cyan]Excel Data ID:[/] {excel_id}   |   "
            f"[bold magenta]Internal LS Task ID:[/] {internal_id}\n"
            f"[bold yellow]Label Target:[/] {label_val}   |   "
            f"[bold white]Status:[/] {status}"
        )
        try:
            widget = self.query_one("#active-task-info", Static)
            widget.update(info_text)
        except Exception:
            pass


class LabelStudioTUI(App):
    """Aplikasi TUI Modern & Komprehensif untuk Label Studio Auto-Annotation Bot."""

    TITLE = "🤖 Label Studio Auto-Annotator"
    SUB_TITLE = "Modern & Functional TUI Dashboard"
    CSS = """
    Screen {
        background: #0d1117;
        color: #c9d1d9;
    }

    /* Layout Main Containers */
    #app-body {
        height: 100%;
        width: 100%;
    }

    #sidebar {
        width: 38;
        height: 100%;
        background: #161b22;
        border-right: solid #30363d;
        padding: 1 1;
    }

    #main-content {
        width: 1fr;
        height: 100%;
        padding: 1 1;
    }

    /* Section Headers */
    .section-title {
        text-style: bold;
        color: #58a6ff;
        border-bottom: solid #30363d;
        margin-bottom: 1;
        padding-bottom: 0;
    }

    /* Form Inputs */
    .field-label {
        color: #8b949e;
        margin-top: 1;
    }

    Input {
        background: #0d1117;
        border: tall #30363d;
        color: #f0f6fc;
        height: 3;
        margin-bottom: 0;
    }

    Input:focus {
        border: tall #58a6ff;
    }

    /* Control Buttons */
    .btn-container {
        margin-top: 1;
        height: auto;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
        border: none;
        height: 3;
        text-style: bold;
    }

    #btn-start {
        background: #238636;
        color: #ffffff;
    }
    #btn-start:hover {
        background: #2ea043;
    }

    #btn-pause {
        background: #d29922;
        color: #ffffff;
    }
    #btn-pause:hover {
        background: #e3b341;
    }

    #btn-stop {
        background: #da3633;
        color: #ffffff;
    }
    #btn-stop:hover {
        background: #f85149;
    }

    #btn-test {
        background: #1f6feb;
        color: #ffffff;
    }
    #btn-test:hover {
        background: #388bfd;
    }

    /* Dashboard Stats Grid */
    #stats-grid {
        layout: horizontal;
        height: 5;
        margin-bottom: 1;
    }

    StatCard {
        width: 1fr;
        height: 100%;
        background: #161b22;
        border: solid #30363d;
        margin-right: 1;
        padding: 0 1;
        content-align: center middle;
    }

    StatCard:last-child {
        margin-right: 0;
    }

    .stat-title {
        color: #8b949e;
        text-align: center;
        width: 100%;
    }

    .stat-value {
        text-style: bold;
        text-align: center;
        width: 100%;
    }

    #stat-total .stat-value { color: #58a6ff; }
    #stat-success .stat-value { color: #3fb950; }
    #stat-failed .stat-value { color: #f85149; }
    #stat-progress .stat-value { color: #d29922; }

    /* Progress & Active Task Box */
    #progress-container {
        background: #161b22;
        border: solid #30363d;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }

    #status-banner {
        color: #a5d6ff;
        text-style: bold;
        margin-bottom: 1;
    }

    ProgressBar {
        width: 100%;
        margin-bottom: 1;
    }

    ActiveTaskCard {
        background: #0d1117;
        border: solid #30363d;
        padding: 1;
        margin-top: 1;
        height: auto;
    }

    .card-header {
        color: #d2a8ff;
        text-style: bold;
        margin-bottom: 1;
    }

    .active-info {
        color: #c9d1d9;
    }

    /* Log Box */
    #log-container {
        height: 1fr;
        background: #161b22;
        border: solid #30363d;
        padding: 0;
    }

    #log-header {
        background: #21262d;
        color: #8b949e;
        padding: 0 1;
        text-style: bold;
    }

    RichLog {
        height: 1fr;
        background: #0d1117;
        color: #c9d1d9;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("s", "toggle_start", "Start / Pause", show=True),
        Binding("x", "stop_process", "Stop", show=True),
        Binding("c", "test_connection", "Test API", show=True),
        Binding("l", "clear_logs", "Clear Logs", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        # State variables
        self.bot_is_running = False
        self.bot_is_paused = False
        self.stop_requested = False

        # Metrics
        self.total_tasks = 0
        self.success_count = 0
        self.failed_count = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-body"):
            # SIDEBAR
            with ScrollableContainer(id="sidebar"):
                yield Label("⚙️ KONFIGURASI BOT", classes="section-title")

                yield Label("Label Studio URL:", classes="field-label")
                yield Input(
                    value=os.getenv("LABEL_STUDIO_URL", "https://bdsrc.binus.ac.id/label-studio/"),
                    id="input-url",
                    placeholder="https://..."
                )

                yield Label("API Key:", classes="field-label")
                yield Input(
                    value=os.getenv("LABEL_STUDIO_API_KEY", ""),
                    id="input-apikey",
                    password=True,
                    placeholder="Masukkan API Key..."
                )

                yield Label("Project ID:", classes="field-label")
                yield Input(
                    value=str(os.getenv("LABEL_STUDIO_PROJECT_ID", "20")),
                    id="input-projectid",
                    placeholder="20"
                )

                yield Label("Excel Data File:", classes="field-label")
                yield Input(
                    value=os.getenv("EXCEL_FILE", "Annotated_Tweets_Cleaned.xlsx"),
                    id="input-excel",
                    placeholder="Annotated_Tweets_Cleaned.xlsx"
                )

                yield Label("Filter JSON File:", classes="field-label")
                yield Input(
                    value=os.getenv("ID_FILTER_FILE", "test_data.json"),
                    id="input-filter",
                    placeholder="test_data.json"
                )

                yield Label("Min - Max Delay (Detik):", classes="field-label")
                with Horizontal():
                    yield Input(value="15", id="input-mindelay", placeholder="15")
                    yield Input(value="30", id="input-maxdelay", placeholder="30")

                with Vertical(classes="btn-container"):
                    yield Button("🔌 Test Connection", id="btn-test", variant="primary")
                    yield Button("▶️ Start Annotation", id="btn-start", variant="success")
                    yield Button("⏸️ Pause", id="btn-pause", variant="warning", disabled=True)
                    yield Button("⏹️ Stop Process", id="btn-stop", variant="error", disabled=True)

            # MAIN DASHBOARD CONTENT
            with Vertical(id="main-content"):
                # STATS CARDS GRID
                with Horizontal(id="stats-grid"):
                    yield StatCard("TOTAL TARGET", "0", id="stat-total")
                    yield StatCard("BERHASIL", "0", id="stat-success")
                    yield StatCard("GAGAL", "0", id="stat-failed")
                    yield StatCard("PROGRESS", "0%", id="stat-progress")

                # PROGRESS & ACTIVE TASK PANEL
                with Vertical(id="progress-container"):
                    yield Label(" Status Bot: Idle (Siap Dijalankan)", id="status-banner")
                    yield ProgressBar(total=100, show_percentage=True, id="main-progressbar")
                    yield ActiveTaskCard(id="active-task-card")

                # LOG PANEL
                with Vertical(id="log-container"):
                    yield Label("📜 LIVE ENGINE LOGS", id="log-header")
                    yield RichLog(id="rich-log", highlight=True, markup=True)

        yield Footer()

    def on_mount(self) -> None:
        """Dipanggil saat UI pertama kali dirender."""
        self.log_message("[bold green][SYS][/] TUI Dashboard Siap. Tekan [bold yellow]Start Annotation[/] untuk mulai.")

    def log_message(self, message: str) -> None:
        """Menambahkan log berwarna ke widget RichLog."""
        timestamp = time.strftime("%H:%M:%S")
        log_widget = self.query_one("#rich-log", RichLog)
        log_widget.write(f"[dim]{timestamp}[/] {message}")

    # ================= EVENT HANDLERS ================= #

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn-test":
            self.action_test_connection()
        elif button_id == "btn-start":
            self.action_toggle_start()
        elif button_id == "btn-pause":
            self.action_toggle_pause()
        elif button_id == "btn-stop":
            self.action_stop_process()

    def action_clear_logs(self) -> None:
        log_widget = self.query_one("#rich-log", RichLog)
        log_widget.clear()
        self.log_message("[dim]Log telah dibersihkan.[/]")

    def action_test_connection(self) -> None:
        """Menguji koneksi ke Label Studio API."""
        url = self.query_one("#input-url", Input).value.strip()
        api_key = self.query_one("#input-apikey", Input).value.strip()
        project_id = self.query_one("#input-projectid", Input).value.strip()

        if not api_key:
            self.log_message("[bold red][ERROR][/] API Key tidak boleh kosong!")
            return

        self.log_message(f"[bold cyan][TEST][/] Menghubungkan ke {url} (Project ID: {project_id})...")
        self.test_connection_worker(url, api_key, project_id)

    @work(exclusive=True, thread=True)
    def test_connection_worker(self, url: str, api_key: str, project_id: str) -> None:
        try:
            ls = LabelStudio(base_url=url, api_key=api_key)
            tasks_gen = ls.tasks.list(project=int(project_id))
            tasks_sample = list(tasks_gen)
            self.call_from_thread(
                self.log_message,
                f"[bold green][TEST SUCCESS][/] Terhubung! Ditemukan {len(tasks_sample)} task di Project {project_id}."
            )
        except Exception as e:
            self.call_from_thread(
                self.log_message,
                f"[bold red][TEST FAILED][/] Gagal terhubung: {e}"
            )

    def action_toggle_start(self) -> None:
        if not self.bot_is_running:
            self.start_annotation_process()

    def action_toggle_pause(self) -> None:
        if self.bot_is_running:
            self.bot_is_paused = not self.bot_is_paused
            btn_pause = self.query_one("#btn-pause", Button)
            status_banner = self.query_one("#status-banner", Label)

            if self.bot_is_paused:
                btn_pause.label = "▶️ Resume"
                status_banner.update(" Status Bot: PAUSED (Dihentikan Sementara)")
                self.log_message("[bold yellow][PAUSE][/] Eksekusi dihentikan sementara.")
            else:
                btn_pause.label = "⏸️ Pause"
                status_banner.update(" Status Bot: RUNNING (Sedang Memproses)")
                self.log_message("[bold green][RESUME][/] Eksekusi dilanjutkan kembali.")

    def action_stop_process(self) -> None:
        if self.bot_is_running:
            self.stop_requested = True
            self.log_message("[bold red][STOP][/] Permintaan penghentian dikirim...")

    def start_annotation_process(self) -> None:
        self.bot_is_running = True
        self.bot_is_paused = False
        self.stop_requested = False

        # Toggle Button States
        self.query_one("#btn-start", Button).disabled = True
        self.query_one("#btn-pause", Button).disabled = False
        self.query_one("#btn-stop", Button).disabled = False

        # Lock inputs
        self.set_inputs_disabled(True)

        url = self.query_one("#input-url", Input).value.strip()
        api_key = self.query_one("#input-apikey", Input).value.strip()
        project_id = self.query_one("#input-projectid", Input).value.strip()
        excel_file = self.query_one("#input-excel", Input).value.strip()
        filter_file = self.query_one("#input-filter", Input).value.strip()
        
        try:
            min_delay = int(self.query_one("#input-mindelay", Input).value.strip())
            max_delay = int(self.query_one("#input-maxdelay", Input).value.strip())
        except ValueError:
            min_delay, max_delay = 15, 30

        self.query_one("#status-banner", Label).update(" Status Bot: RUNNING (Memuat Data...)")
        self.log_message("[bold green][START][/] Memulai proses auto-anotasi...")
        
        # Launch Worker Thread
        self.annotation_worker(url, api_key, project_id, excel_file, filter_file, min_delay, max_delay)

    def set_inputs_disabled(self, disabled: bool) -> None:
        for input_id in ["#input-url", "#input-apikey", "#input-projectid", "#input-excel", "#input-filter", "#input-mindelay", "#input-maxdelay"]:
            self.query_one(input_id, Input).disabled = disabled

    # ================= ANNOTATION WORKER THREAD ================= #

    @work(exclusive=True, thread=True)
    def annotation_worker(
        self, url: str, api_key: str, project_id: str,
        excel_file: str, filter_file: str, min_delay: int, max_delay: int
    ) -> None:
        # 1. Validation & Setup
        if not api_key:
            self.call_from_thread(self.log_message, "[bold red][ERROR][/] API Key tidak boleh kosong!")
            self.call_from_thread(self.finish_annotation_process, False)
            return

        # 2. Connect to Label Studio
        self.call_from_thread(self.log_message, f"🔗 Menghubungkan ke Label Studio ({url})...")
        try:
            ls = LabelStudio(base_url=url, api_key=api_key)
            proj_id_int = int(project_id)
            all_tasks = list(ls.tasks.list(project=proj_id_int))
            
            id_mapping = {}
            for task in all_tasks:
                d_id = str(task.data.get('id', ''))
                if d_id:
                    id_mapping[d_id] = task.id

            self.call_from_thread(
                self.log_message, 
                f"[bold green][OK][/] Berhasil memetakan {len(id_mapping)} task dari Label Studio."
            )
        except Exception as e:
            self.call_from_thread(self.log_message, f"[bold red][ERROR][/] Gagal memetakan Label Studio tasks: {e}")
            self.call_from_thread(self.finish_annotation_process, False)
            return

        # 3. Read Filter JSON
        self.call_from_thread(self.log_message, f"📄 Membaca file filter ID: {filter_file}")
        try:
            with open(filter_file, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict) and "dari" in data and "sampai" in data:
                target_ids = list(range(data["dari"], data["sampai"] + 1))
            elif isinstance(data, list):
                target_ids = data
            else:
                raise ValueError("Format JSON harus berupa list [ID1, ID2] atau {\"dari\": X, \"sampai\": Y}")
        except Exception as e:
            self.call_from_thread(self.log_message, f"[bold red][ERROR][/] Gagal membaca filter file: {e}")
            self.call_from_thread(self.finish_annotation_process, False)
            return

        # 4. Read Excel File
        self.call_from_thread(self.log_message, f"📊 Membaca file Excel data: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            self.call_from_thread(self.log_message, f"[bold red][ERROR][/] Gagal membaca Excel file: {e}")
            self.call_from_thread(self.finish_annotation_process, False)
            return

        # Filter DF
        df_filtered = df[df['id'].isin(target_ids)]
        total = len(df_filtered)

        if total == 0:
            self.call_from_thread(self.log_message, "[bold yellow][WARN][/] Tidak ada ID cocok di file Excel. Selesai.")
            self.call_from_thread(self.finish_annotation_process, True)
            return

        self.total_tasks = total
        self.success_count = 0
        self.failed_count = 0

        # Update initial stats UI
        self.call_from_thread(self.update_stats_ui)

        # 5. Annotation Loop
        processed = 0
        for index, row in df_filtered.iterrows():
            # Check stop request
            if self.stop_requested:
                self.call_from_thread(self.log_message, "[bold red][STOPPED][/] Proses dihentikan oleh pengguna.")
                break

            # Check pause state
            while self.bot_is_paused and not self.stop_requested:
                time.sleep(0.5)

            if self.stop_requested:
                break

            excel_id = str(row['id'])
            label_val = row.get('sentiment', None)

            if pd.isna(row['id']) or pd.isna(label_val):
                continue

            internal_task_id = id_mapping.get(excel_id)
            label_val_str = str(label_val)

            # Update Active Task Card UI
            self.call_from_thread(
                self.update_active_task_card,
                excel_id, str(internal_task_id or "TIDAK DITEMUKAN"), label_val_str, "Memproses Send API..."
            )

            if not internal_task_id:
                self.call_from_thread(
                    self.log_message,
                    f"[bold red][-] Gagal:[/] Data ID {excel_id} tidak ada di Project {project_id} Label Studio."
                )
                self.failed_count += 1
                processed += 1
                self.call_from_thread(self.update_stats_ui)
                continue

            # Payload
            result_payload = [{
                "from_name": "sentiment",
                "to_name": "text",
                "type": "choices",
                "value": {"choices": [label_val_str]}
            }]

            try:
                ls.annotations.create(
                    id=internal_task_id,
                    task=internal_task_id,
                    result=result_payload
                )
                self.success_count += 1
                self.call_from_thread(
                    self.log_message,
                    f"[bold green][+] Berhasil:[/] Data ID {excel_id} (Internal Task #{internal_task_id}) -> '{label_val_str}'"
                )
                self.call_from_thread(
                    self.update_active_task_card,
                    excel_id, str(internal_task_id), label_val_str, "[bold green]Berhasil dikirim![/]"
                )
            except Exception as e:
                self.failed_count += 1
                self.call_from_thread(
                    self.log_message,
                    f"[bold red][-] Gagal:[/] Data ID {excel_id} -> {e}"
                )
                self.call_from_thread(
                    self.update_active_task_card,
                    excel_id, str(internal_task_id), label_val_str, f"[bold red]Error: {e}[/]"
                )

            processed += 1
            self.call_from_thread(self.update_stats_ui)

            # Delay Countdown Handling (human-like pause)
            if processed < total and not self.stop_requested:
                delay_sec = random.randint(min_delay, max_delay)
                for remaining in range(delay_sec, 0, -1):
                    if self.stop_requested:
                        break
                    while self.bot_is_paused and not self.stop_requested:
                        self.call_from_thread(
                            self.update_status_banner,
                            " Status Bot: PAUSED (Dihentikan Sementara)"
                        )
                        time.sleep(0.5)
                    
                    if self.stop_requested:
                        break

                    self.call_from_thread(
                        self.update_status_banner,
                        f" Status Bot: Jeda Acak ({remaining} detik tersisa sebelum task berikutnya...)"
                    )
                    time.sleep(1)

        self.call_from_thread(self.finish_annotation_process, True)

    def update_stats_ui(self) -> None:
        """Mengupdate widget statistik dashboard."""
        self.query_one("#stat-total", StatCard).update_value(str(self.total_tasks))
        self.query_one("#stat-success", StatCard).update_value(str(self.success_count))
        self.query_one("#stat-failed", StatCard).update_value(str(self.failed_count))

        done_cnt = self.success_count + self.failed_count
        pct = (done_cnt / self.total_tasks * 100) if self.total_tasks > 0 else 0
        self.query_one("#stat-progress", StatCard).update_value(f"{pct:.1f}%")

        progress_bar = self.query_one("#main-progressbar", ProgressBar)
        progress_bar.total = max(1, self.total_tasks)
        progress_bar.progress = done_cnt

    def update_status_banner(self, text: str) -> None:
        self.query_one("#status-banner", Label).update(text)

    def update_active_task_card(self, excel_id: str, internal_id: str, label_val: str, status: str) -> None:
        card = self.query_one("#active-task-card", ActiveTaskCard)
        card.update_info(excel_id, internal_id, label_val, status)

    def finish_annotation_process(self, completed_normally: bool) -> None:
        self.bot_is_running = False
        self.bot_is_paused = False
        self.stop_requested = False

        self.query_one("#btn-start", Button).disabled = False
        self.query_one("#btn-pause", Button).disabled = True
        self.query_one("#btn-stop", Button).disabled = True
        self.query_one("#btn-pause", Button).label = "⏸️ Pause"

        self.set_inputs_disabled(False)

        if completed_normally:
            self.update_status_banner(" Status Bot: Selesai (Proses Berakhir)")
            self.log_message(
                f"[bold green]🎉 PROSES SELESAI![/] Total: {self.total_tasks} | "
                f"Berhasil: {self.success_count} | Gagal: {self.failed_count}"
            )
        else:
            self.update_status_banner(" Status Bot: Terhenti dengan Error / Dibatalkan")


def main():
    app = LabelStudioTUI()
    app.run()


if __name__ == '__main__':
    main()

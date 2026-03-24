import sys
import asyncio
import logging
import qasync
from PySide6.QtWidgets import QApplication
from app.coordinator import AppCoordinator
from app.settings import AppSettings
from ui.main_window import MainWindow
from ui.styles import DARK_THEME

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("openoats.log", encoding="utf-8"),
    ],
)
# Keep our own modules at INFO
for _mod in ("app", "audio", "transcription", "intelligence", "storage"):
    logging.getLogger(_mod).setLevel(logging.INFO)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    settings = AppSettings()

    # First-run onboarding
    if not settings.recording_consent_acknowledged:
        from ui.onboarding_dialog import OnboardingDialog
        dialog = OnboardingDialog(settings)
        if dialog.exec() != OnboardingDialog.DialogCode.Accepted:
            sys.exit(0)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    coordinator = AppCoordinator(settings=settings)
    window = MainWindow(coordinator)
    window.show()

    from ui.system_tray import SystemTray
    window._tray = SystemTray(main_window=window, coordinator=coordinator)

    async def _startup():
        if coordinator.kb:
            window._kb_label.setText("Indexing KB...")
            await coordinator.kb.index(
                progress_cb=lambda done, total: window._kb_label.setText(
                    f"Indexing KB: {done}/{total}"
                )
            )
            window._kb_label.setText(f"KB: {coordinator.kb.chunk_count} chunks")

    loop.call_soon(lambda: asyncio.ensure_future(_startup()))

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()

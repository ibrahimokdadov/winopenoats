import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication
from app.coordinator import AppCoordinator
from app.settings import AppSettings
from ui.main_window import MainWindow
from ui.styles import DARK_THEME


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

    async def _startup():
        if coordinator.kb:
            window._kb_label.setText("Indexing KB...")
            await coordinator.kb.index(
                progress_cb=lambda done, total: window._kb_label.setText(
                    f"Indexing KB: {done}/{total}"
                )
            )
            window._kb_label.setText(f"KB: {len(coordinator.kb._chunks)} chunks")

    loop.call_soon(lambda: asyncio.ensure_future(_startup()))

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()

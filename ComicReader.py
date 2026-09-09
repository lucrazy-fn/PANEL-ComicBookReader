from panel_app.auth_views import AuthWindow
from panel_app.community_views import CommunityWindow
from panel_app.moderation_views import ModerationWindow
from panel_app.publishing_views import PublishDialog
from panel_app.library_views import LibraryWindow
from panel_app.reader_views import LangWindow, ReaderWindow, WebtoonViewer

__all__ = [
    "AuthWindow", "CommunityWindow", "LangWindow", "LibraryWindow",
    "ModerationWindow", "PublishDialog", "ReaderWindow", "WebtoonViewer",
]

if __name__ == "__main__":
    app = LibraryWindow()
    app.mainloop()

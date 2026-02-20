from .receive_title import ReceiveTitleView
from .remove_from_watchlist import RemoveFromWatchlistView
from .sign import SignUpView
from .title_detail import TitleDetailView
from .title_list import TitleListView
from .toogle_episode_watched import ToggleEpisodeWatchedView
from .update_user_title_state import UpdateUserTitleStateView

__all__ = [
    "SignUpView",
    "UpdateUserTitleStateView",
    "TitleListView",
    "TitleDetailView",
    "ReceiveTitleView",
    "ToggleEpisodeWatchedView",
    "RemoveFromWatchlistView",
]

from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_simplejwt import views as jwt_views
from .views.drf_postgres import PosgresDataListCreateView
from .views.drf_mongo import MongoDataListCreateView
from .views.drf_serials import MongoDataSerialListCreateView
from .views.admin.login import MyLoginView
from .views.admin.dashboard import Dashboard
from .views.admin.list_torrent import ListTorrent
from .views.admin.torrents_delete import TorrentsDelete
from .views.admin.comments import ListComments
from .views.admin.adult_filter import AdultFilter
from .views.admin.tpb import ListTpb
from .views.admin.backup import BackupSetting
from .views.xmlview import XMLView
from .views.admin.eztv import ListEztv
from .views.drf_share_list import ShareList
from .views.admin.yts_torrent import YtsTorrent

urlpatterns = [
    path('admin/', MyLoginView.as_view(), name='auth_page'),
    path('admin/dashboard/', Dashboard.as_view(), name='main_page'),
    path('admin/list', ListTorrent.as_view(), name='list_torrent_page'),
    path('admin/torr_delete', TorrentsDelete.as_view(), name='torrent_delete_page'),
    path('admin/list_comments', ListComments.as_view(), name='list_comments_page'),
    path('admin/adult_filter', AdultFilter.as_view(), name='adult_filter_page'),
    path('admin/tpb', ListTpb.as_view(), name='tpb_page'),
    path('admin/backup', BackupSetting.as_view(), name='backup_page'),
    path('trackers/', XMLView.as_view(), name = 'xml_page'),
    path('admin/eztv', ListEztv.as_view(), name='eztv_page'),
    path('admin/yts', YtsTorrent.as_view(), name='yts_page'),


    path('api/list/', MongoDataListCreateView().as_view(), name='data_list_mongo'),
    path('api/list/serials/', MongoDataSerialListCreateView().as_view(), name='data_list_serials'),
    path('api/list/share/', ShareList().as_view(), name='share_list'),
    path('api/comment/', PosgresDataListCreateView().as_view(), name='data_comment_postgres'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += staticfiles_urlpatterns()
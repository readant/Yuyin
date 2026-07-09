"""古籍式文案配置"""


class Texts:
    """古籍式文案"""

    # 应用信息
    APP_NAME = "余音"
    APP_SLOGAN = "余音绕梁，三日不绝"
    APP_DESCRIPTION = "雅乐相伴，知音相随"

    # 导航栏
    NAV_PLAYER = "听曲"
    NAV_LIBRARY = "藏曲阁"
    NAV_FINGERING = "指法"
    NAV_LYRICS = "词韵"
    NAV_RHYTHM = "节拍"
    NAV_SETTINGS = "雅室"

    # 播放器
    PLAYER_TITLE = "正在聆听"
    PLAYER_NO_PLAY = "静候知音"
    PLAYER_SELECT_SONG = "请选择一曲"
    PLAYER_LYRICS = "词韵"
    PLAYER_VINYL = "唱片"

    # 音乐库
    LIBRARY_TITLE = "藏曲阁"
    LIBRARY_SEARCH = "寻曲..."
    LIBRARY_ALL = "全部"
    LIBRARY_FAVORITE = "倾心之音"
    LIBRARY_RECENT = "近日所闻"
    LIBRARY_IMPORT = "纳入曲库"
    LIBRARY_EMPTY = "曲库空空，待君填满"

    # 歌词编辑器
    LYRICS_TITLE = "词韵编辑"
    LYRICS_LIST = "词句"
    LYRICS_EDIT = "编辑区"
    LYRICS_IMPORT = "导入词韵"
    LYRICS_SAVE = "保存"
    LYRICS_SAVE_AS = "另存为"
    LYRICS_ADD = "添加词句"
    LYRICS_DELETE = "删除词句"
    LYRICS_SEARCH = "寻词"
    LYRICS_PREVIEW = "预览"
    LYRICS_EMPTY = "暂无词韵"
    LYRICS_PLACEHOLDER = "输入词句..."

    # 指法查询
    FINGERING_TITLE = "指法图鉴"
    FINGERING_KEY = "调性"
    FINGERING_TYPE = "指法"
    FINGERING_NOTE = "音符"

    # 节奏训练
    RHYTHM_TITLE = "节拍修炼"
    RHYTHM_BPM = "速度"
    RHYTHM_TIME_SIG = "拍号"
    RHYTHM_PATTERN = "节拍"
    RHYTHM_START = "开始"
    RHYTHM_STOP = "停"
    RHYTHM_TAP = "击节"
    RHYTHM_RESET = "重置"
    RHYTHM_FREE = "自由修炼"
    RHYTHM_FOLLOW = "跟练模式"
    RHYTHM_CHALLENGE = "挑战模式"
    RHYTHM_SCORE = "分数"
    RHYTHM_STATS = "修炼记录"

    # 设置
    SETTINGS_TITLE = "雅室陈设"
    SETTINGS_THEME = "主题雅趣"
    SETTINGS_AUDIO = "音律设置"
    SETTINGS_ABOUT = "关于"
    SETTINGS_DEVICE = "输出"
    SETTINGS_EQUALIZER均衡器 = "均衡器"

    # 操作提示
    CONFIRM_DELETE = "确定要删除吗？"
    CONFIRM_TITLE = "确认"
    SUCCESS_SAVE = "保存成功"
    SUCCESS_LOAD = "加载成功"
    ERROR_LOAD = "加载失败"
    ERROR_SAVE = "保存失败"

    # 通用按钮
    BTN_OK = "确定"
    BTN_CANCEL = "取消"
    BTN_YES = "是"
    BTN_NO = "否"
    BTN_CLOSE = "关闭"
    BTN_BACK = "返回"
    BTN_NEXT = "下一步"
    BTN_FINISH = "完成"

    # 播放控制
    PLAY = "播放"
    PAUSE = "暂停"
    STOP = "停止"
    PREV = "上一曲"
    NEXT = "下一曲"

    # 时间
    NOW_PLAYING = "正在播放"
    TOTAL_TIME = "总时长"
    REMAIN_TIME = "剩余时间"

    # 音量
    VOLUME = "音量"
    MUTE = "静音"

    # 歌曲信息
    SONG_TITLE = "曲名"
    SONG_ARTIST = "演奏者"
    SONG_ALBUM = "专辑"
    SONG_DURATION = "时长"

    # 主题
    THEME_SHUI_MO = "水墨素雅"
    THEME_ZHU_SHA = "朱砂浓墨"
    THEME_QING_CI = "青瓷素雅"

    # 拍号
    TIME_2_4 = "二四拍"
    TIME_3_4 = "三四拍"
    TIME_4_4 = "四四拍"
    TIME_6_8 = "六八拍"

    # 节拍模式
    PATTERN_POP = "流行"
    PATTERN_ROCK = "摇滚"
    PATTERN_WALTZ = "华尔兹"
    PATTERN_MARCH = "进行曲"
    PATTERN_BALLAD = "抒情"

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        """获取文案"""
        return getattr(cls, key, default)


# 全局文案实例
texts = Texts()
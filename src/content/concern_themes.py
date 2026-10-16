"""悩み特化の高単価記事（常設販売）のテーマ定義 —— 仕事運・お金特化版。

12.uranai の実売上（2026-10時点・1,200本）で売れたのは「転職・天職占い」「人生使命占い」などの
仕事・人生系で、恋愛特化（1,980円）は売上0だった。そのため仕事系（水・金）とお金系（日）に絞る。
手書きの初期テーマを使い切ると、Geminiが新テーマを自動生成し data/concern_themes_dynamic.json に追記する。
"""

import json
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
DYNAMIC_THEMES_FILE = _ROOT / "data" / "concern_themes_dynamic.json"
# リポジトリへのコミットは PAT の権限次第で失敗する（403）ため、Actions キャッシュで
# 運ばれる output/ 配下にも同じ内容を書き、どちらか残っていればテーマを失わないようにする。
DYNAMIC_THEMES_CACHE = _ROOT / "output" / "concern_themes_dynamic.json"
_DYNAMIC_FILES = (DYNAMIC_THEMES_FILE, DYNAMIC_THEMES_CACHE)

# 仕事・キャリアの悩み（水曜・金曜枠）。売れた2テーマ（転職・天職／人生使命）を先頭に置く。
CONCERN_THEMES = [
    {
        "key": "career",
        "title": "転職・天職占い｜あなたの本当の才能と動くべき時期",
        "audience": "今の仕事を続けるべきか転職すべきか迷っている、自分の天職を知りたい",
        "keyword": "仕事と天職",
        "core_question": "あなたが転職すべきか、あなたの本当の才能と天職、動くべき時期はいつか",
        "bullets": "・あなたに眠る本当の才能・天職\n・転職すべきか、留まるべきか\n・キャリアが大きく動く時期",
        "hashtags": ["転職占い", "仕事占い", "天職", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "life_mission",
        "title": "人生使命占い｜あなたがこの世で果たすべき天命と、本当に輝ける道",
        "audience": "このままの人生でいいのか、自分は何のために働いているのか分からなくなっている",
        "keyword": "人生の使命",
        "core_question": "あなたがこの人生で果たすべき使命は何か、本当に輝ける道はどこにあるのか",
        "bullets": "・星が示すあなたの天命と生まれ持った役割\n・本当に輝ける仕事・生き方の方向\n・使命に向かって動き出すべき時期",
        "hashtags": ["天職", "使命", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "aptitude",
        "title": "適職占い｜あなたに向いている仕事・向いていない仕事",
        "audience": "何をやっても長続きしない、自分にどんな仕事が合っているのか分からない",
        "keyword": "あなたの適職",
        "core_question": "あなたに本当に向いている仕事は何か、逆に避けるべき仕事は何か",
        "bullets": "・あなたの星が示す適職と、その理由\n・向いていない働き方・職場の特徴\n・適職に近づくために今できる一歩",
        "hashtags": ["適職", "適職診断", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "quit_job",
        "title": "仕事を辞めたい占い｜今辞めるべき？続けるべき？",
        "audience": "毎朝仕事に行くのがつらく、辞めたい気持ちと不安の間で揺れている",
        "keyword": "辞めるべきかの答え",
        "core_question": "今の仕事を辞めるべきか続けるべきか、辞めるならいつが良いのか",
        "bullets": "・今の職場があなたに与えている本当の影響\n・辞めた場合と続けた場合、それぞれの未来\n・決断すべきベストなタイミング",
        "hashtags": ["仕事辞めたい", "退職", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "workplace_relations",
        "title": "職場の人間関係占い｜苦手なあの人との関係はどうなる？",
        "audience": "上司や同僚との関係に疲れていて、職場に行くのが憂うつ",
        "keyword": "職場の人間関係",
        "core_question": "職場の人間関係はこれからどうなるのか、苦手な相手とどう付き合えばいいのか",
        "bullets": "・あの人があなたに抱いている本当の評価\n・関係が好転する時期ときっかけ\n・あなたが今すぐ変えられる立ち回り方",
        "hashtags": ["職場の人間関係", "人間関係", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "promotion",
        "title": "昇進・出世占い｜あなたが評価される時期と方法",
        "audience": "頑張っているのに評価されない、昇進や昇給のチャンスがいつ来るのか知りたい",
        "keyword": "昇進のタイミング",
        "core_question": "あなたが正当に評価され、昇進・昇給するのはいつか、そのために何をすべきか",
        "bullets": "・あなたが評価されにくい本当の理由\n・昇進・昇給のチャンスが来る時期\n・評価を一気に引き上げる行動",
        "hashtags": ["昇進", "出世", "仕事運", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "independence",
        "title": "独立・起業占い｜会社を辞めて一人でやっていける？",
        "audience": "いつか独立・起業したいと思いながら、踏み出す勇気とタイミングが分からない",
        "keyword": "独立・起業の可能性",
        "core_question": "あなたは独立・起業で成功できるのか、動くならいつ・何から始めるべきか",
        "bullets": "・あなたが独立に向いているか、星が示す答え\n・成功しやすい事業の方向性\n・踏み出すべき時期と、それまでの準備",
        "hashtags": ["独立", "起業", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "side_job",
        "title": "副業占い｜あなたが副業で稼げる分野と始める時期",
        "audience": "本業だけでは将来が不安で、副業を始めたいが何をすればいいか分からない",
        "keyword": "副業の適性",
        "core_question": "あなたが副業で稼げるのはどんな分野か、いつから始めるとうまくいくのか",
        "bullets": "・あなたの才能が収入に変わりやすい副業の分野\n・副業が軌道に乗る時期\n・始める前に避けるべき落とし穴",
        "hashtags": ["副業", "副収入", "仕事占い", "占い", "星座占い"],
        "price": 1980,
    },
]


# お金・金運の悩み（日曜枠）。12.uranai では恋愛特化の枠だったが、恋愛は売上0のため置き換えた。
MONEY_THEMES = [
    {
        "key": "money_luck",
        "group": "money",
        "title": "金運占い｜あなたにお金が入ってくる流れ",
        "audience": "お金の不安から解放されたい、自分の金運と豊かになる方法を知りたい",
        "keyword": "金運の流れ",
        "core_question": "あなたの金運はこれからどうなるのか、お金を引き寄せるにはどうすべきか",
        "bullets": "・あなたの金運が上昇する時期\n・あなたにお金が入ってくる流れの作り方\n・避けるべき金運を下げる行動",
        "hashtags": ["金運", "金運アップ", "占い", "星座占い", "開運"],
        "price": 1980,
    },
    {
        "key": "money_income_up",
        "group": "money",
        "title": "収入アップ占い｜あなたの収入が増える時期と道",
        "audience": "がんばって働いているのに収入が増えず、この先もずっと同じなのか不安",
        "keyword": "収入が増える道",
        "core_question": "あなたの収入はいつ・どうやって増えるのか、星はどの道を示しているのか",
        "bullets": "・あなたの収入が増え始める時期\n・あなたに向いた稼ぎ方（本業・副業・転職）\n・収入の天井を作っている思い込み",
        "hashtags": ["収入アップ", "金運", "仕事運", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "money_saving",
        "group": "money",
        "title": "お金が貯まる占い｜なぜかお金が残らない本当の理由",
        "audience": "節約しているつもりなのに、気づくといつもお金が残っていない",
        "keyword": "お金が貯まらない理由",
        "core_question": "なぜあなたのお金は貯まらないのか、貯まる体質に変わるにはどうすればいいのか",
        "bullets": "・あなたのお金が出ていく星回りのクセ\n・貯まる流れに切り替わる時期\n・今日から変えられるお金の習慣",
        "hashtags": ["貯金", "節約", "金運", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "money_anxiety",
        "group": "money",
        "title": "お金の不安占い｜この先お金に困らない？",
        "audience": "老後や将来のお金のことを考えると、夜眠れないほど不安になる",
        "keyword": "将来のお金の不安",
        "core_question": "あなたはこの先お金に困らずに生きていけるのか、不安を消すために何をすべきか",
        "bullets": "・星が示すあなたの生涯の金運の流れ\n・お金の不安が強まる時期と、和らぐ時期\n・不安を安心に変える具体的な一歩",
        "hashtags": ["お金の不安", "金運", "将来の不安", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "money_windfall",
        "group": "money",
        "title": "臨時収入占い｜思わぬお金が舞い込むタイミング",
        "audience": "思いがけないお金のチャンスを逃さず、流れに乗りたい",
        "keyword": "臨時収入の時期",
        "core_question": "あなたに臨時収入や思わぬお金のチャンスが訪れるのはいつか、どう受け取ればいいのか",
        "bullets": "・臨時収入やチャンスが来やすい時期\n・お金の縁を運んでくる人・場所\n・チャンスを逃さないための準備",
        "hashtags": ["臨時収入", "金運", "金運アップ", "占い", "星座占い"],
        "price": 1980,
    },
    {
        "key": "money_block",
        "group": "money",
        "title": "お金のブロック占い｜豊かさを遠ざけている本当の原因",
        "audience": "お金を稼ぐこと・受け取ることに、どこか罪悪感や抵抗がある",
        "keyword": "お金のブロック",
        "core_question": "あなたの豊かさを遠ざけている心のブロックは何か、どうすれば外せるのか",
        "bullets": "・あなたが無意識に抱えているお金のブロック\n・ブロックが外れて流れが変わる時期\n・豊かさを受け取るための小さな習慣",
        "hashtags": ["お金のブロック", "豊かさ", "金運", "占い", "星座占い"],
        "price": 1980,
    },
]

_GROUPS = {"general": CONCERN_THEMES, "money": MONEY_THEMES}


def load_dynamic_themes() -> list[dict]:
    """自動生成された動的テーマを読み込む（リポジトリ側とキャッシュ側をkeyでマージ）。"""
    merged: list[dict] = []
    seen = set()
    for path in _DYNAMIC_FILES:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for t in data:
            key = t.get("key") if isinstance(t, dict) else None
            if key and key not in seen:
                merged.append(t)
                seen.add(key)
    return merged


def load_all_themes(group: str = "general") -> list[dict]:
    """指定グループの手書き＋動的テーマを、keyの重複を除いて返す。

    group を持たない動的テーマは "general"（仕事）として扱う。
    """
    themes = list(_GROUPS.get(group, CONCERN_THEMES))
    seen = {t["key"] for t in themes}
    for t in load_dynamic_themes():
        if t.get("key") and t["key"] not in seen and t.get("group", "general") == group:
            themes.append(t)
            seen.add(t["key"])
    return themes


def save_dynamic_theme(theme: dict) -> None:
    """動的テーマを1件追記し、リポジトリ側とキャッシュ側の両方へ保存する。"""
    current = load_dynamic_themes()
    current.append(theme)
    body = json.dumps(current, ensure_ascii=False, indent=2)
    for path in _DYNAMIC_FILES:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


def get_theme(key: str) -> dict | None:
    for group in _GROUPS:
        for t in load_all_themes(group):
            if t["key"] == key:
                return t
    return None

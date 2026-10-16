"""星座占いコンテンツ生成"""

import random
from datetime import date, timedelta
from pathlib import Path
from typing import Tuple

from src.content.gemini_client import GeminiClient
from src.utils.date_utils import get_week_range_str, get_week_label, get_date_str, get_month_str
from src.utils.logger import get_logger

logger = get_logger("horoscope_generator")

PROMPT_DIR = Path(__file__).parent / "prompts"
PAID_BOUNDARY = "---PAID_BOUNDARY---"
STRATEGY_FILE = Path(__file__).parent.parent.parent / "output" / "strategy" / "current_strategy.txt"

WEEKDAY_JP = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

# タイトルは (型, 重み)。型の構造と重みは 12.uranai の販売実績（売れた型を多く出す）を引き継ぎ、
# 切り口の言葉を仕事運・お金向けに置き換えた。低重みの型は探索枠として残す。
WEEKLY_TITLE_PATTERNS = [
    ("【保存版】{sign}の週間仕事運 {week}｜仕事・お金・人間関係", 3),
    ("{sign}の今週の仕事運（{week}）｜{angle}", 3),
    ("【{sign}】週間仕事運 {week}｜{angle}", 1),
    ("{sign}さんへ。今週の仕事とお金の正直な運勢 {week}", 1),
    ("【{sign}】{week} 当たりすぎ注意の週間仕事運", 1),
]

WEEKLY_ANGLE_WORDS = [
    ("今週のキャリアの転機を読む", 3),
    ("仕事・お金・評価の全真実", 2),
    ("上司の評価と金運の完全鑑定", 2),
    ("今週の職場であなたに起きること", 1),
    ("チャンスが来る人・来ない人", 1),
    ("攻める日・守る日", 1),
]

MONTHLY_TITLE_PATTERNS = [
    ("【保存版】{sign}の{month}仕事運・財運｜{angle}", 4),
    ("【{sign}】{month} 仕事運・財運完全版｜{angle}", 1),
    ("{sign}さんへ。{month}の仕事とお金の本当の運勢", 1),
    ("【{sign}・{month}】当たりすぎ注意の仕事運・財運完全版", 1),
]

MONTHLY_ANGLE_WORDS = [
    ("天体メッセージ×タロット完全版", 4),
    ("転職・昇進・お金の完全解説", 1),
    ("今月あなたの仕事に何が起きるか", 1),
    ("転職・昇進の転機？詳細鑑定で答えを出す", 1),
    ("今月こそ動くべき理由とお金の戦略", 1),
]


def _load_prompt(filename: str) -> str:
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")


def _load_style_guide() -> str:
    """全鑑定に共通する人間らしい文体ガイドを読み込む"""
    try:
        return (PROMPT_DIR / "_writing_style.txt").read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _load_strategy() -> str:
    """パフォーマンス分析から生成された戦略コンテキストを読み込む"""
    if STRATEGY_FILE.exists():
        try:
            return STRATEGY_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return ""


def _random_stars(min_val: int = 2, max_val: int = 5) -> str:
    n = random.randint(min_val, max_val)
    return "★" * n + "☆" * (5 - n)


def _pick(weighted: list) -> str:
    items, weights = zip(*weighted)
    return random.choices(items, weights=weights, k=1)[0]


def generate_weekly_title(sign: dict, week_label: str) -> str:
    """週次記事の引き込むタイトルを生成（25〜30文字）"""
    return _pick(WEEKLY_TITLE_PATTERNS).format(
        sign=sign["name"], week=week_label, angle=_pick(WEEKLY_ANGLE_WORDS)
    )


def generate_monthly_title(sign: dict, month_str: str) -> str:
    """月次記事の引き込むタイトルを生成"""
    return _pick(MONTHLY_TITLE_PATTERNS).format(
        sign=sign["name"], month=month_str, angle=_pick(MONTHLY_ANGLE_WORDS)
    )


# 日次で売れた3本はすべて「｜切り口」付きの型。切り口なしの型（〜さんへ。正直な運勢／当たりすぎ注意）と
# 【保存版】はPV下位で売上0のため外した。「今日動くべき時間と避ける時間」はPV・スキとも最下位。
DAILY_TITLE_PATTERNS = [
    ("【{sign}】{date}の仕事運｜{angle}", 3),
    ("{sign}の今日の仕事運（{date}）｜{angle}", 3),
    ("【{sign}・{date}】{angle}", 1),
]

DAILY_ANGLE_WORDS = [
    ("今日の仕事の転機を読む", 4),
    ("仕事とお金の流れの全真実", 3),
    ("仕事のパワータイムはいつ？完全鑑定", 1),
    ("上司の本音と今日の金運", 1),
    ("今日、仕事の流れが変わる瞬間", 1),
]


def generate_daily_title(sign: dict, date_str: str) -> str:
    """日次記事のタイトルを生成"""
    return _pick(DAILY_TITLE_PATTERNS).format(
        sign=sign["name"], date=date_str, angle=_pick(DAILY_ANGLE_WORDS)
    )


class HoroscopeGenerator:
    def __init__(self, client: GeminiClient):
        self._client = client

    def generate_daily(self, sign: dict, target_date: date = None) -> Tuple[str, str]:
        """日次占い（note投稿用・300円）→ (ティーザー, 有料コンテンツ) を返す"""
        if target_date is None:
            target_date = date.today()

        strategy = _load_strategy()
        strategy_context = f"\n【今週の改善戦略（分析データに基づく）】\n{strategy}\n" if strategy else ""

        prompt_template = _load_prompt("daily_horoscope.txt")
        prompt = prompt_template.format(
            sign_name=sign["name"],
            symbol=sign["symbol"],
            period=sign["period"],
            element=sign["element"],
            ruling_planet=sign["ruling_planet"],
            keywords="・".join(sign["keywords"]),
            date_str=get_date_str(target_date),
            weekday=WEEKDAY_JP[target_date.weekday()],
            love_stars=_random_stars(2, 5),
            work_stars=_random_stars(2, 5),
            money_stars=_random_stars(2, 5),
            overall_stars=_random_stars(3, 5),
            strategy_context=strategy_context,
            style_guide=_load_style_guide(),
        )

        raw = self._client.generate(prompt, max_tokens=32768, temperature=0.88, thinking_budget=2048)
        teaser, paid = _split_content(raw)
        logger.info(
            f"[日次] {sign['name']} 生成完了: "
            f"ティーザー{len(teaser)}文字 / 有料{len(paid)}文字"
        )
        return teaser, paid

    def generate_daily_batch(self, signs: list, target_date: date = None) -> dict:
        """複数星座の日次占いを1回のAPI呼び出しでまとめて生成する。

        星座ごとに個別に呼ぶとGemini無料枠（1モデル20リクエスト/日）を
        すぐ使い切るため、まとめて生成して呼び出し回数を減らす。
        戻り値: {sign_en: (teaser, paid)}。取り出せなかった星座は含めない。
        """
        if target_date is None:
            target_date = date.today()

        strategy = _load_strategy()
        strategy_context = f"\n【今日の改善戦略（分析データに基づく）】\n{strategy}\n" if strategy else ""

        signs_block = "\n".join(
            f"- キー: {s['en']} / {s['name']}（{s['symbol']}）{s['period']}生まれ / "
            f"支配星: {s['ruling_planet']} / エレメント: {s['element']} / "
            f"キーワード: {'・'.join(s['keywords'])}"
            for s in signs
        )

        prompt = _load_prompt("daily_horoscope_batch.txt").format(
            date_str=get_date_str(target_date),
            weekday=WEEKDAY_JP[target_date.weekday()],
            style_guide=_load_style_guide(),
            strategy_context=strategy_context,
            signs_block=signs_block,
        )

        # 思考型モデルは考える過程にも出力枠を使い、4星座ぶん（約2万字）を書き切る前に上限に達する。
        # 出力上限を最大にし、考える量を抑えて本文に枠を回す。
        raw = self._client.generate(prompt, max_tokens=65536, temperature=0.88, thinking_budget=2048)
        results = _split_batch(raw, [s["en"] for s in signs])

        missing = [s["en"] for s in signs if s["en"] not in results]
        if missing:
            logger.warning(f"[日次バッチ] 取り出せなかった星座: {missing}")
        for sign_en, (teaser, paid) in results.items():
            logger.info(
                f"[日次バッチ] {sign_en} 生成完了: "
                f"ティーザー{len(teaser)}文字 / 有料{len(paid)}文字"
            )
        return results

    def generate_concern(self, sign: dict, theme: dict) -> Tuple[str, str]:
        """悩み特化の高単価記事 → (ティーザー, 有料コンテンツ) を返す"""
        strategy = _load_strategy()
        strategy_context = f"\n【売れる記事のための改善戦略（実績データに基づく）】\n{strategy}\n" if strategy else ""

        prompt_template = _load_prompt("concern_reading.txt")
        prompt = prompt_template.format(
            strategy_context=strategy_context,
            sign_name=sign["name"],
            symbol=sign["symbol"],
            period=sign["period"],
            element=sign["element"],
            ruling_planet=sign["ruling_planet"],
            keywords="・".join(sign["keywords"]),
            concern_title=theme["title"],
            concern_audience=theme["audience"],
            concern_keyword=theme["keyword"],
            concern_core_question=theme["core_question"],
            concern_bullets=theme["bullets"],
            price=theme["price"],
            style_guide=_load_style_guide(),
        )
        raw = self._client.generate(prompt, max_tokens=65536, temperature=0.86, thinking_budget=2048)
        teaser, paid = _split_content(raw)
        logger.info(
            f"[悩み特化:{theme['key']}] {sign['name']} 生成完了: "
            f"ティーザー{len(teaser)}文字 / 有料{len(paid)}文字"
        )
        return teaser, paid

    def generate_daily_free_ranking(self, target_date: date = None) -> str:
        """無料の集客用「今日の12星座ランキング」を生成して本文を返す"""
        if target_date is None:
            target_date = date.today()

        prompt_template = _load_prompt("daily_free_ranking.txt")
        prompt = prompt_template.format(
            date_str=get_date_str(target_date),
            weekday=WEEKDAY_JP[target_date.weekday()],
            style_guide=_load_style_guide(),
        )
        content = self._client.generate(prompt, max_tokens=8192, temperature=0.9).strip()
        # 無料記事に境界が混入したら除去
        content = content.replace(PAID_BOUNDARY, "").strip()
        logger.info(f"[無料ランキング] 生成完了: {len(content)}文字")
        return content

    def generate_weekly(
        self,
        sign: dict,
        week_start: date,
        week_end: date,
    ) -> Tuple[str, str]:
        """週次占い → (ティーザー, 有料コンテンツ) を返す"""
        week_range = get_week_range_str(week_start, week_end)
        week_label = get_week_label(week_start)

        strategy = _load_strategy()
        strategy_context = f"\n【今週の改善戦略（分析データに基づく）】\n{strategy}\n" if strategy else ""

        prompt_template = _load_prompt("weekly_horoscope.txt")
        prompt = prompt_template.format(
            sign_name=sign["name"],
            symbol=sign["symbol"],
            period=sign["period"],
            element=sign["element"],
            ruling_planet=sign["ruling_planet"],
            keywords="・".join(sign["keywords"]),
            week_start=week_range.split("〜")[0],
            week_end=week_range.split("〜")[1],
            week_label=week_label,
            love_stars=_random_stars(2, 5),
            work_stars=_random_stars(2, 5),
            money_stars=_random_stars(2, 5),
            overall_stars=_random_stars(3, 5),
            strategy_context=strategy_context,
            style_guide=_load_style_guide(),
        )

        raw = self._client.generate(prompt, max_tokens=32768, temperature=0.87, thinking_budget=2048)
        teaser, paid = _split_content(raw)
        logger.info(
            f"[週次] {sign['name']} 生成完了: "
            f"ティーザー{len(teaser)}文字 / 有料{len(paid)}文字"
        )
        return teaser, paid

    def generate_monthly(
        self,
        sign: dict,
        target_date: date = None,
    ) -> Tuple[str, str]:
        """月次占い → (ティーザー, 有料コンテンツ) を返す"""
        if target_date is None:
            target_date = date.today()

        themes = [
            "キャリアの転換点", "評価と昇進", "財運と豊かさ",
            "才能の開花", "職場の縁と協力者", "収入の流れを変える",
            "働き方の再設計", "天職に近づく",
        ]
        theme = random.choice(themes)

        # 週別カレンダー用の日付（月の各週末日）
        month_end = (target_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        week1_end = min(7, month_end.day)
        week2_end = min(14, month_end.day)
        week3_end = min(21, month_end.day)

        strategy = _load_strategy()
        strategy_context = f"\n【今月の改善戦略（分析データに基づく）】\n{strategy}\n" if strategy else ""

        prompt_template = _load_prompt("monthly_horoscope.txt")
        prompt = prompt_template.format(
            sign_name=sign["name"],
            symbol=sign["symbol"],
            period=sign["period"],
            element=sign["element"],
            ruling_planet=sign["ruling_planet"],
            keywords="・".join(sign["keywords"]),
            month_str=get_month_str(target_date),
            love_stars=_random_stars(2, 5),
            work_stars=_random_stars(2, 5),
            money_stars=_random_stars(2, 5),
            overall_stars=_random_stars(3, 5),
            theme=theme,
            week1_end=week1_end,
            week2_end=week2_end,
            week3_end=week3_end,
            strategy_context=strategy_context,
            style_guide=_load_style_guide(),
        )

        raw = self._client.generate(prompt, max_tokens=65536, temperature=0.85, thinking_budget=2048)
        teaser, paid = _split_content(raw)
        logger.info(
            f"[月次] {sign['name']} 生成完了: "
            f"ティーザー{len(teaser)}文字 / 有料{len(paid)}文字"
        )
        return teaser, paid


def _split_batch(raw: str, expected_keys: list) -> dict:
    """バッチ生成の出力を ===SIGN:キー=== で星座ごとに分割する。

    生成が途中で打ち切られた場合に備え、本文が短すぎるものは
    不完全とみなして採用しない（中途半端な記事を公開しないため）。
    """
    import re

    results = {}
    parts = re.split(r"===\s*SIGN\s*:\s*([A-Za-z_]+)\s*===", raw)
    # parts = [先頭ゴミ, キー1, 本文1, キー2, 本文2, ...]
    for i in range(1, len(parts) - 1, 2):
        key = parts[i].strip().lower()
        body = parts[i + 1]
        if key not in expected_keys:
            continue
        teaser, paid = _split_content(body)
        if len(paid) < 800:
            logger.warning(f"[日次バッチ] {key} は本文が短すぎるため不採用（{len(paid)}文字）")
            continue
        results[key] = (teaser, paid)
    return results


def _split_content(raw: str) -> Tuple[str, str]:
    """PAID_BOUNDARY で分割してティーザーと有料コンテンツを返す"""
    if PAID_BOUNDARY in raw:
        parts = raw.split(PAID_BOUNDARY, 1)
        return parts[0].strip(), parts[1].strip()
    logger.warning("PAID_BOUNDARY が見つかりません。先頭300文字をティーザーとして使用します。")
    return raw[:300], raw[300:]

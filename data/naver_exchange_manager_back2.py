"""
네이버 검색 환율 수집기

JPY/KRW : 일본 엔화 (100엔 기준)
USD/KRW : 미국 달러 (1달러 기준)

수집 방식:
requests + BeautifulSoup

반환 형식:
{
    "USD/KRW": {
        "price": 1335.40,
        "change": -76.8,
        "change_pct": -5.43,
        "change_label": "하락"
    }
}

주의:
- get_rate()는 기존 코드와의 호환성을 위해 현재 환율(float)만 반환한다.
- fetch_all()은 현재 환율, 변동폭, 등락률을 함께 반환한다.
"""

import logging
import re

import requests
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class NaverExchangeManager:

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            )
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 엔화 URL (100엔 기준)
        self.jpy_url = (
            "https://search.naver.com/search.naver?"
            "sm=mtb_drt&where=m&"
            "query=%EC%9D%BC%EB%B3%B8%ED%99%98%EC%9C%A8"
        )

        # 달러 URL (1달러 기준)
        self.usd_url = (
            "https://search.naver.com/search.naver?"
            "where=nv&sm=top_sug.ase&fbm=0&acr=1&"
            "acq=usd%ED%99%98&qdt=0&ie=utf8&"
            "query=USD+%ED%99%98%EC%9C%A8&"
            "ackey=q1504zld"
        )

        self.rate = {
            "USD/KRW": None,
            "JPY/KRW": None
        }

        # 마지막으로 정상 수집한 상세 시세
        self.quotes = {
            "USD/KRW": None,
            "JPY/KRW": None
        }

    @staticmethod
    def _to_float(text):
        """문자열에서 부호가 포함된 숫자를 추출한다."""
        if not text:
            return None

        cleaned = text.replace(",", "").replace("\u2212", "-")
        match = re.search(r"[+-]?\d+(?:\.\d+)?", cleaned)

        if not match:
            return None

        return float(match.group(0))

    @classmethod
    def _parse_price_info(cls, html):
        """
        네이버 .price_info 영역에서 가격/변동폭/등락률을 추출한다.

        예:
        <strong class="price">1,335.40</strong>
        <span class="u_hc">하락</span>
        <span class="price_gap">76.8<span>(-5.43%)</span></span>
        """
        soup = BeautifulSoup(html, "html.parser")

        price_info = soup.select_one("div.price_info")

        print("======= 프라이스",price_info)

        # 일부 페이지 구조 변경에 대비한 대체 선택자
        root = price_info if price_info else soup

        price_element = root.select_one("strong.price")
        if price_element is None:
            return None

        price = cls._to_float(price_element.get_text(" ", strip=True))
        if price is None:
            return None

        label_element = root.select_one(
            "[data-price-change-label], span.u_hc"
        )
        change_label = (
            label_element.get_text(" ", strip=True)
            if label_element else ""
        )

        gap_element = root.select_one(
            "[data-price-change], span.price_gap"
        )

        change = None
        change_pct = None

        if gap_element is not None:
            # 직접 자식 텍스트만 추출해야 중첩된 등락률과 섞이지 않는다.
            direct_text = "".join(
                str(child).strip()
                for child in gap_element.find_all(string=True, recursive=False)
            )

            # 직접 텍스트가 비어 있는 변형 구조도 처리한다.
            if not direct_text:
                full_text = gap_element.get_text(" ", strip=True)
                percent_match = re.search(
                    r"\(?\s*[+-]?\d+(?:\.\d+)?\s*%\s*\)?",
                    full_text
                )
                direct_text = (
                    full_text[:percent_match.start()]
                    if percent_match else full_text
                )

            change = cls._to_float(direct_text)

            gap_text = gap_element.get_text(" ", strip=True)
            percent_match = re.search(
                r"\(?\s*([+-]?\d+(?:\.\d+)?)\s*%\s*\)?",
                gap_text
            )
            if percent_match:
                change_pct = float(percent_match.group(1))

        # 네이버 HTML의 변동폭은 부호 없이 제공될 수 있으므로
        # '상승/하락' 라벨을 기준으로 부호를 보정한다.
        if change is not None:
            if "하락" in change_label:
                change = -abs(change)
            elif "상승" in change_label:
                change = abs(change)
            elif "보합" in change_label:
                change = 0.0

        # 등락률에 부호가 없다면 변동폭의 방향을 적용한다.
        if change_pct is not None:
            if "하락" in change_label:
                change_pct = -abs(change_pct)
            elif "상승" in change_label:
                change_pct = abs(change_pct)
            elif "보합" in change_label:
                change_pct = 0.0

        
        print("굿굿굿 뿅",price,change,change_pct,change_label)


        return {
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "change_label": change_label or None
        }

    def get_quote(self, url, name):
        """환율 상세 정보 전체를 조회한다."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding

            quote = self._parse_price_info(response.text)

            if quote is None:
                log.warning("%s 가격 정보를 찾을 수 없음", name)
                return None

            log.info(
                "%s: %.2f원, 변동 %s, 등락률 %s%% (%s)",
                name,
                quote["price"],
                quote["change"],
                quote["change_pct"],
                quote["change_label"]
            )
            return quote

        except requests.RequestException as e:
            log.error("%s 환율 조회 실패: %s", name, e)
            return None
        except Exception:
            log.exception("%s 데이터 파싱 중 오류 발생", name)
            return None

    def get_rate(self, url, name):
        """
        기존 호출부와의 호환성을 유지한다.
        상세 데이터는 self._last_quote에 저장하고 가격(float)만 반환한다.
        """
        self._last_quote = self.get_quote(url, name)
        return self._last_quote["price"] if self._last_quote else None

    def get_jpy_rate(self):
        quote = self.get_quote(self.jpy_url, "JPY/KRW (100엔)")
        if quote is not None:
            self.quotes["JPY/KRW"] = quote
            self.rate["JPY/KRW"] = quote["price"]

        return self.rate["JPY/KRW"]

    def get_usd_rate(self):
        quote = self.get_quote(self.usd_url, "USD/KRW (1달러)")
        if quote is not None:
            self.quotes["USD/KRW"] = quote
            self.rate["USD/KRW"] = quote["price"]

        return self.rate["USD/KRW"]

    def fetch_all(self):
        """USD/JPY 환율을 조회하고 상세 시세 딕셔너리를 반환한다."""
        self.get_jpy_rate()
        self.get_usd_rate()

        result = {}

        for symbol in ("USD/KRW", "JPY/KRW"):
            quote = self.quotes.get(symbol)

            if quote is not None:
                # 호출부가 원본 객체를 변경하지 않도록 복사해 반환한다.
                result[symbol] = dict(quote)

        return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    manager = NaverExchangeManager()
    result = manager.fetch_all()

    print("\n========== 네이버 환율 조회 ==========")

    for symbol, quote in result.items():
        unit = " (100엔)" if symbol == "JPY/KRW" else ""
        print(
            f"{symbol}{unit}: {quote['price']:,.2f}원 | "
            f"변동: {quote['change']} | "
            f"등락률: {quote['change_pct']}% | "
            f"방향: {quote['change_label']}"
        )

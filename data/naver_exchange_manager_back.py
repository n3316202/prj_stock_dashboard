
"""
네이버 검색 환율 수집기

JPY/KRW : 일본 엔화 (100엔 기준)
USD/KRW : 미국 달러 (1달러 기준)

수집 방식:
requests + BeautifulSoup
"""

import logging
import requests

from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class NaverExchangeManager:

    def __init__(self):

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            )
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # ------------------------------------------------
        # 엔화 URL (100엔 기준)
        # ------------------------------------------------
        self.jpy_url = (
            "https://search.naver.com/search.naver?"
            "sm=mtb_drt&where=m&"
            "query=%EC%9D%BC%EB%B3%B8%ED%99%98%EC%9C%A8"
        )

        # ------------------------------------------------
        # 달러 URL (1달러 기준)
        # ------------------------------------------------
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

    # ====================================================
    # 네이버 환율 가격 추출
    # ====================================================

    def get_rate(self, url, name):

        try:

            response = self.session.get(
                url,
                timeout=5
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # 네이버 환율 가격
            price_element = soup.select_one(
                "strong.price"
            )

            if price_element is None:

                log.warning(
                    "%s 가격 정보를 찾을 수 없음",
                    name
                )

                return None

            rate_text = price_element.get_text(
                strip=True
            )

            rate = float(
                rate_text.replace(",", "")
            )

            log.info(
                "%s : %s원",
                name,
                rate
            )

            return rate

        except Exception as e:

            log.error(
                "%s 환율 조회 실패: %s",
                name,
                e
            )

            return None

    # ====================================================
    # 일본 엔화 (100엔 기준)
    # ====================================================

    def get_jpy_rate(self):

        rate = self.get_rate(
            self.jpy_url,
            "JPY/KRW (100엔)"
        )

        if rate is not None:

            self.rate["JPY/KRW"] = rate

        return self.rate["JPY/KRW"]

    # ====================================================
    # 미국 달러 (1달러 기준)
    # ====================================================

    def get_usd_rate(self):

        rate = self.get_rate(
            self.usd_url,
            "USD/KRW (1달러)"
        )

        if rate is not None:

            self.rate["USD/KRW"] = rate

        return self.rate["USD/KRW"]

    # ====================================================
    # 전체 환율 조회
    # ====================================================

    def fetch_all(self):

        jpy = self.get_jpy_rate()
        usd = self.get_usd_rate()

        result = {}

        if usd is not None:

            result["USD/KRW"] = {
                "price": usd,
                "change": None,
                "change_pct": None
            }

        if jpy is not None:

            result["JPY/KRW"] = {
                "price": jpy,
                "change": None,
                "change_pct": None
            }

        return result


# ========================================================
# 단독 실행 테스트
# ========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    manager = NaverExchangeManager()

    result = manager.fetch_all()

    print("\n========== 네이버 환율 조회 ==========")

    if result.get("USD/KRW"):

        print(
            f"달러 : {result['USD/KRW']['price']:,.2f}원"
        )

    if result.get("JPY/KRW"):

        print(
            f"엔화 : {result['JPY/KRW']['price']:,.2f}원 (100엔)"
        )

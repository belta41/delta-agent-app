import os


class DeltaConnector:
    def __init__(self, api_key="", api_secret="", use_testnet=True):
        self.api_key = api_key or os.getenv("DELTA_API_KEY", "")
        self.api_secret = api_secret or os.getenv("DELTA_API_SECRET", "")
        self.client = None
        self.base_url = "https://api.india.delta.exchange"

        if self.api_key and self.api_secret:
            try:
                from delta_rest_client import DeltaRestClient, OrderType
                self.client = DeltaRestClient(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                )
                self.OrderType = OrderType
            except ImportError:
                pass

    def place_order(self, product_id, size, side, order_type="market_order", limit_price=None, leverage=20):
        if not self.client:
            print(f"MOCK: {side} {size} of {product_id}")
            return {"status": "mock"}

        ot = self.OrderType.MARKET
        if order_type == "limit_order":
            ot = self.OrderType.LIMIT

        try:
            self.client.set_leverage(product_id, leverage)
        except Exception as e:
            print(f"leverage error: {e}")

        params = {"product_id": product_id, "size": size, "side": side, "order_type": ot}
        if limit_price:
            params["limit_price"] = limit_price
        return self.client.place_order(**params)

    def get_ticker(self, symbol="BTCUSD"):
        if not self.client:
            return {"mark_price": 0}
        return self.client.get_ticker(symbol)

    def get_balances(self, asset_id=None):
        if not self.client:
            return []
        if asset_id:
            return self.client.get_balances(asset_id)
        assets = self.client.get_assets()
        all_bal = []
        for a in assets:
            try:
                bal = self.client.get_balances(a["id"])
                if bal and float(bal.get("balance", 0)) > 0:
                    all_bal.append(bal)
            except:
                continue
        return all_bal

    def get_positions(self):
        if not self.client:
            return []
        return self.client.get_positions()

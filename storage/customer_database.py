class CustomerDataBase:
    """客户数据库（模拟）"""
    
    def __init__(self):
        self.customers = {
            "user001": {
                "name": "张三",
                "level": "VIP",
                "phone": "1234567890",
                "email": "zhangsan@example.com",
            },
            "user002": {
                "name": "李四",
                "level": "VIP",
                "phone": "0123456789",
                "email": "lisi@example.com",
            },
        }
        
        self.orders = {
            "user001": [
                {
                    "order_id": "order00101",
                    "product": "高端会员套餐",
                    "price": 999.0,
                    "date": "2026-01-01",
                    "status": "已完成"
                },
                {
                    "order_id": "order00102",
                    "product": "专属服务包",
                    "price": 199.0,
                    "date": "2026-01-10",
                    "status": "已完成"
                }
            ],
            "user002": [
                {
                    "order_id": "order00201",
                    "product": "VIP权益包",
                    "price": 599.0,
                    "date": "2026-01-05",
                    "status": "已完成"
                },
                {
                    "order_id": "order00202",
                    "product": "续费套餐",
                    "price": 899.0,
                    "date": "2026-01-15",
                    "status": "待支付"
                }
            ]
        }
    
    def get_customer_info(self, user_id: str) -> dict:
        """通过user_id获取客户基础信息"""
        if user_id not in self.customers:
            print(f"提示：未找到ID为{user_id}的客户信息")
            return None
        return self.customers[user_id]
    
    def get_customer_orders(self, user_id: str) -> list:
        """通过user_id获取客户订单信息"""
        if user_id not in self.orders:
            print(f"提示：未找到ID为{user_id}的订单信息")
            return []
        return self.orders[user_id]

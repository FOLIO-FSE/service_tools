
class OrderMigrationBase():

    @staticmethod
    def instantiate_purchase_order(poNumber):
        return {"poNumber": poNumber}
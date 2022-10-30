from pydblite.sqlite import Database, Table

class in_mem_cache:
    def __init__(self): 
        db = Database(":memory:")
        self.table = Table('rfid_config', db)
        self.table.create(('container_id', 'TEXT'), ('latitude', 'REAL'), ('longitude', 'REAL'), ('origin_id', 'TEXT'), ('destination_id', 'TEXT'), ('status', 'TEXT'))
        self.table.open()
        self.table.insert(container_id='14004A267C04', latitude=23.05, longitude=1.84, origin_id='N', destination_id='N', status='InProgress') 
        self.table.insert(container_id='0796AE44FA81', latitude=23.05, longitude=1.84, origin_id='N', destination_id='N', status='InProgress') 
        self.table.commit()

    def get(self, id):
        records = self.table(container_id=id)
        return records[0]
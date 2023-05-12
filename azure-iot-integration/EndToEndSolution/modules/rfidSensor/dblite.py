from pydblite.sqlite import Database, Table

class in_mem_cache:
    def __init__(self): 
        db = Database(":memory:")
        self.table = Table('rfid_config', db)
        self.table.create(('tag_id', 'TEXT'), ('container_id', 'TEXT'), ('latitude', 'REAL'), ('longitude', 'REAL'), ('origin_id', 'TEXT'), ('destination_id', 'TEXT'), ('status', 'TEXT'), ('type', 'TEXT'))
        self.table.open()
        self.table.insert(tag_id="14004A267C04", container_id='Container-X072862', latitude=39.09, longitude=-94.57, origin_id='N', destination_id='N', status='InProgress', type='container_tracking') 
        self.table.insert(tag_id="000000160412", container_id='Container-X072862', latitude=35.11, longitude=-89.97, origin_id='N', destination_id='N', status='InProgress', type='container_tracking') 
        self.table.insert(tag_id="000000160513", container_id='Container-X072862', latitude=32.29, longitude=-90.18, origin_id='N', destination_id='N', status='InProgress', type='container_tracking') 
        self.table.commit()

    def get(self, id):
        records = self.table(tag_id=id)
        return records[0]
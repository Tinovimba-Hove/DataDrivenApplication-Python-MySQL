import pymysql
import yaml
from pathlib import Path


class baseObject:
    def setup(self):
        config = yaml.safe_load(Path("config.example.yml").read_text())
        self.config = config
        self.tn = self.config['tables'][type(self).__name__]
        self.conn = None
        self.cur = None
        self.pk = None
        self.fields = []
        self.errors = []
        self.data = []
        self.establishConnection()
        self.getFields()
    def establishConnection(self): 
        config = self.config
        #print(config)
        self.conn = pymysql.connect(host=config['db']['host'], port=config['db']['port'], user=config['db']['user'],
                    passwd=config['db']['passwd'], db=config['db']['db'], autocommit=True)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)  

    def set(self,d):
        self.data.append(d)
    def getFields(self):
        sql = f'''DESCRIBE `{self.tn}`;'''
        self.cur.execute(sql)
        for row in self.cur:
            if row['Extra'] == 'auto_increment':
                self.pk  = row['Field']
            else:
                self.fields.append(row['Field'])
    def insert(self,n=0):
        count = 0
        vals = []
        sql = f"INSERT INTO `{self.tn}` ("
        for field in self.fields:
            sql += f"`{field}`,"
            vals.append(self.data[n][field])
            count +=1
        sql = sql[0:-1] + ') VALUES ('
        tokens = ("%s," * count)[0:-1]
        sql += tokens + ');'
        #print(sql,vals)
        self.cur.execute(sql,vals)
        self.data[n][self.pk] = self.cur.lastrowid
    def createBlank(self):
        d = {}
        for field in self.fields:
            d[field] = ''
        self.set(d)
    def getById(self,id):
        sql = f"Select * from `{self.tn}` where `{self.pk}` = %s" 
        print(sql,id)
        self.cur.execute(sql,(id))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def getAll(self):
        sql = f"Select * from `{self.tn}`" 
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def truncate(self):
        sql = f"TRUNCATE TABLE `{self.tn}`" 
        self.cur.execute(sql)
    def getByField(self,field,val):
        sql = f"Select * from `{self.tn}` where `{field}` = %s" 
        #print(sql,val)
        self.cur.execute(sql,(val))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def update(self,n=0):
        vals=[]
        fvs=''
        for field in self.fields:
            if field in self.data[n].keys():
                fvs += f"`{field}`=%s,"
                vals.append(self.data[n][field])
        fvs=fvs[:-1]
        sql=f"UPDATE `{self.tn}` SET {fvs} WHERE `{self.pk}` = %s"
        vals.append(self.data[n][self.pk])
        #print(sql,vals)
        self.cur.execute(sql,vals)
    def deleteById(self,id):
        sql = f"Delete from `{self.tn}` where `{self.pk}` = %s" 
        self.cur.execute(sql,(id))
        self.cur.connection.commit()

   
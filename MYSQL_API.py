import pymysql
import json


# MODEL
class aoi_allresults_detail:
    def __init__(self):
        pass

    def all_list(self):
        awm_key = "awm_key"
        sn = "sn"
        aoi_start = "aoi_start"
        aoi_end = "aoi_end"
        aoi_cv_lead_time = "aoi_cv_lead_time"
        aoi_op_lead_time = "aoi_op_lead_time"
        pass_or_failure = "pass_or_failure"
        list = [awm_key, sn, aoi_start, aoi_end, aoi_cv_lead_time, aoi_op_lead_time, pass_or_failure]
        return list

    def key_list(self):
        awm_key = "awm_key"
        sn = "sn"
        list = [awm_key, sn]
        return list


# Control
class SQL_aoi_allresults_detail(aoi_allresults_detail):
    def __init__(self, IP, port, user, password, database):
        super().__init__()
        # 資料庫連線設定
        self.IP = IP
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.db = pymysql.connect(host=str(self.IP), port=int(self.port), user=str(self.user),
                                  passwd=str(self.password), db=str(self.database), charset='utf8')
        # 建立操作游標
        self.cursor = self.db.cursor()

    # 獲取列名
    def get_column(self, table_name):
        sql = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        self.cursor.execute(sql)
        self.column_data = self.cursor.fetchall()
        # 打印列名
        # print(self.column_data)

        # 将元组列表转换为字典
        data_dict = {item[0]: None for item in self.column_data}
        # 将字典转换为 JSON 字符串
        column_json = json.dumps(data_dict)
        # 将 JSON 字符串转换为字典
        column_json = json.loads(column_json)
        # 打印 JSON 字符串
        return (column_json)

    # 獲取某表單全部資料
    def get_table_all_data(self, table_name):
        col_json = self.get_column(table_name)
        col_list = self.all_list()
        sql = f'select * from {str(table_name)}'
        self.cursor.execute(sql)
        all_data = self.cursor.fetchall()
        all_data_json = []
        for data in all_data:

            for i in range(0, len(data)):
                col_json[col_list[i]] = data[i]
            all_data_json.append(col_json)
        return (all_data_json)

    # 獲取某表單指定資料
    def get_table_one_data(self, table_name, key):
        col_json = self.get_column(table_name)
        col_list = self.key_list()
        sql = f'select * from {str(table_name)} where '
        for i in range(0, len(col_list)):
            sql = sql + f"{col_list[i]} = '{key[col_list[i]]}'"
            if i < len(col_list) - 1:
                sql = sql + ' and '
        self.cursor.execute(sql)
        data = self.cursor.fetchall()[0]
        col_list = self.all_list()
        for i in range(0, len(data)):
            col_json[col_list[i]] = data[i]
        return col_json

    # 新增資料
    def post_table_one_data(self, table_name, data):
        col_json = self.get_column(table_name)
        col_list = self.all_list()
        sql = f'INSERT INTO {table_name} ' + '('
        for i in range(0, len(col_list)):
            sql = sql + f'{col_list[i]}'
            if i < len(col_list) - 1:
                sql = sql + ","
            else:
                sql = sql + ") Values ("
        for i in range(0, len(col_list)):
            if (type(data[col_list[i]])) == str:
                sql = sql + f"'{data[col_list[i]]}'"
            else:
                sql = sql + f'{data[col_list[i]]}'
            if i < len(col_list) - 1:
                sql = sql + ','
            else:
                sql = sql + ')'
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()


# MODEL
class aoi_ng_detail:
    def __init__(self):
        pass

    def all_list(self):
        awm_key = "awm_key"
        sn = "sn"
        ng1 = "ng1"
        ng2 = "ng2"
        ng3 = "ng3"
        list = [awm_key, sn, ng1, ng2, ng3]
        return list

    def key_list(self):
        awm_key = "awm_key"
        sn = "sn"
        list = [awm_key, sn]
        return list


# Control
class SQL_aoi_ng_detail(aoi_ng_detail):
    def __init__(self, IP, port, user, password, database):
        super().__init__()
        # 資料庫連線設定
        self.IP = IP
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.db = pymysql.connect(host=str(self.IP), port=int(self.port), user=str(self.user),
                                  passwd=str(self.password), db=str(self.database), charset='utf8')
        # 建立操作游標
        self.cursor = self.db.cursor()

    # 獲取列名
    def get_column(self, table_name):
        sql = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        self.cursor.execute(sql)
        self.column_data = self.cursor.fetchall()
        # 打印列名
        # print(self.column_data)

        # 将元组列表转换为字典
        data_dict = {item[0]: None for item in self.column_data}
        # 将字典转换为 JSON 字符串
        column_json = json.dumps(data_dict)
        # 将 JSON 字符串转换为字典
        column_json = json.loads(column_json)
        # 打印 JSON 字符串
        return (column_json)

    # 獲取某表單全部資料
    def get_table_all_data(self, table_name):
        col_json = self.get_column(table_name)
        # print(col_json)
        # print(col_json[self.awm_key])
        col_list = self.all_list()

        sql = f'select * from {str(table_name)}'
        self.cursor.execute(sql)
        all_data = self.cursor.fetchall()
        all_data_json = []
        # print(all_data)
        for data in all_data:
            # print(data)
            for i in range(0, len(data)):
                col_json[col_list[i]] = data[i]
            all_data_json.append(col_json)
        # print(all_data_json)
        return (all_data_json)

    # 獲取某表單指定資料
    def get_table_one_data(self, table_name, key):
        col_json = self.get_column(table_name)
        col_list = self.key_list()
        sql = f'select * from {str(table_name)} where '
        for i in range(0, len(col_list)):
            sql = sql + f"{col_list[i]} = '{key[col_list[i]]}'"
            if i < len(col_list) - 1:
                sql = sql + " and "
        self.cursor.execute(sql)
        data = self.cursor.fetchall()[0]
        col_list = self.all_list()
        for i in range(0, len(data)):
            col_json[col_list[i]] = data[i]
        return col_json

    # 新增資料
    def post_table_one_data(self, table_name, data):
        col_json = self.get_column(table_name)
        col_list = self.all_list()
        sql = f'INSERT INTO {table_name} ' + "("
        for i in range(0, len(col_list)):
            sql = sql + f'{col_list[i]}'
            if i < len(col_list) - 1:
                sql = sql + ","
            else:
                sql = sql + ") Values ("
        for i in range(0, len(col_list)):
            if (type(data[col_list[i]])) == str:
                sql = sql + f"'{data[col_list[i]]}'"
            else:
                sql = sql + f'{data[col_list[i]]}'
            if i < len(col_list) - 1:
                sql = sql + ","
            else:
                sql = sql + ")"

        self.cursor.execute(sql)
        self.db.commit()
        print(sql)


def AOI_all():
    AOI_detail_SQL = SQL_aoi_allresults_detail("140.125.21.65", 3307, 'VIP125', '@VIPvip125', 'VIP125')

    # 調用所有資料
    all_data = AOI_detail_SQL.get_table_all_data(table_name="aoi_allresults_detail")
    print(all_data)
    # 調用單筆資料
    KEY = {
        "awm_key": 'M11-2303001-0050',
        "sn": "1"
    }
    one_data = AOI_detail_SQL.get_table_one_data(table_name="aoi_allresults_detail", key=KEY)
    print(one_data)
    # 新增資料
    data = {
        "awm_key": "M11-2303001-0051",
        "sn": "3",
        "aoi_start": "2023-09-08 20:09:13.000",
        "aoi_end": "2023-09-08 20:09:13.000",
        "aoi_cv_lead_time": 2.2,
        "aoi_op_lead_time": 2,
        "pass_or_failure": True,
    }

    AOI_detail_SQL.post_table_one_data(table_name="aoi_allresults_detail", data=data)


def AOI_ng():
    AOI_NG_detail_SQL = SQL_aoi_ng_detail("140.125.21.65", 3307, 'VIP125', '@VIPvip125', 'VIP125')
    # 調用所有資料
    all_data = AOI_NG_detail_SQL.get_table_all_data(table_name="aoi_ng_detail")
    print(all_data)

    # 調用單筆資料
    KEY = {
        "awm_key": 'M11-2303001-0050',
        "sn": "2"
    }
    one_data = AOI_NG_detail_SQL.get_table_one_data(table_name="aoi_ng_detail", key=KEY)
    print(one_data)

    # 新增資料
    data = {
        "awm_key": "M11-2303001-0051",
        "sn": "3",
        "ng1": "1,2,3",
        "ng2": "",
        "ng3": ""

    }

    AOI_NG_detail_SQL.post_table_one_data(table_name="aoi_ng_detail", data=data)


AOI_all()
# AOI_ng()

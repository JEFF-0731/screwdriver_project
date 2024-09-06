import configparser

class Myini:
    def __init__(self):
        self.Class_Name_AI = list()
        self.Class_Name_All = list()
        self.recipes = list()
        self.ROI_List = list()
        self.MeasureSize_dic = {}
        self.MeasureSize_Area_dic = {}
        self.MeasureSize_Approx_Area_dic = {}
        self.MeasureSize_Approx_ArcLength_dic = {}
        self.Pre_ROI_Dic = {}
        self.NotValid_dic = {}
        self.NotValid_NumberOfVertices_dic = {}
        self.recipe = 'Milwaukee'
        self.Identity_CodeName = []
        self.recipe_model = ''
        self.Camera_Setting = {}

        self.read_ini()


    def read_ini(self):
        print(f'目前的recipe = {self.recipe}')
        config = configparser.ConfigParser()
        config.read('ScrewDrive.ini')
        self.Class_Name_All.clear()
        self.ROI_List.clear()
        self.Class_Name_AI.clear()
        self.Pre_ROI_Dic.clear()
        self.Identity_CodeName.clear()
        self.Identity_CodeName = config['Object_Amount'][self.recipe].split(',')
        print(f'self.Identity_CodeName = {self.Identity_CodeName}')
        self.recipe_model = config['RECIPE_Model'][self.recipe]
        print(f'self.recipe_model = {self.recipe_model}')

        for key in config['RECIPE']:
            self.recipes.append(config['RECIPE'][key])
        # self.recipe = self.recipes[0]
        if f'AITYPE_{self.recipe}' in config:
            for i in config[f'AITYPE_{self.recipe}']:
                self.Class_Name_AI.append(config[f'AITYPE_{self.recipe}'][i])
            # print(f'self.Class_Name_AI = {self.Class_Name_AI}')
            for key in config[f'MeasureSize_{self.recipe}']:
                # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
                number_list = config[f'MeasureSize_{self.recipe}'][key].split(',')
                # 將每個元素轉換為浮點數
                float_numbers = [float(number) for number in number_list]
                self.MeasureSize_dic[key] = float_numbers
            # print(f'self.MeasureSize_dic = {self.MeasureSize_dic}')

            for key in config[f'MeasureSize_Approx_ArcLength_{self.recipe}']:
                # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
                number_list = config[f'MeasureSize_Approx_ArcLength_{self.recipe}'][key].split(',')
                # 將每個元素轉換為浮點數
                float_numbers = [float(number) for number in number_list]
                self.MeasureSize_Approx_ArcLength_dic[key] = float_numbers
            # print(f'self.MeasureSize_Approx_ArcLength_dic = {self.MeasureSize_Approx_ArcLength_dic}')

            for key in config[f'MeasureSize_Approx_Area_{self.recipe}']:
                # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
                number_list = config[f'MeasureSize_Approx_Area_{self.recipe}'][key].split(',')
                # 將每個元素轉換為浮點數
                float_numbers = [float(number) for number in number_list]
                self.MeasureSize_Approx_Area_dic[key] = float_numbers
            # print(f'self.MeasureSize_Approx_Area_dic = {self.MeasureSize_Approx_Area_dic}')
            for key in config[f'NotValid_{self.recipe}']:
                # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
                number_list = config[f'NotValid_{self.recipe}'][key].split(',')
                # 將每個元素轉換為浮點數
                float_numbers = [float(number)*1.01 if k % 2 == 1 else float(number)*0.99 for k, number in enumerate(number_list)]
                self.NotValid_dic[key] = float_numbers
            for key in config[f'NotValid_NumberOfVertices_{self.recipe}']:
                self.NotValid_NumberOfVertices_dic[key] = int(config[f'NotValid_NumberOfVertices_{self.recipe}'][key])
        else:
            for i in config['AITYPE_OtherSets']:
                self.Class_Name_AI.append(config['AITYPE_OtherSets'][i])
            for key in config['MeasureSize_OtherSets']:
                # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
                number_list = config['MeasureSize_OtherSets'][key].split(',')
                # 將每個元素轉換為浮點數
                float_numbers = [float(number) for number in number_list]
                self.MeasureSize_dic[key] = float_numbers
        if f'Pre_ROI_{self.recipe}' in config:
            for k, key in enumerate(self.Identity_CodeName):
                self.Pre_ROI_Dic[key] = [int(x) for x in config[f'Pre_ROI_{self.recipe}'][str(k)].split(',')]

            # for k, key in enumerate(config[f'Pre_ROI_{self.recipe}']):
            #     # print(self.recipe)
            #     self.Pre_ROI_Dic[self.Identity_CodeName[k]] = [int(x) for x in config[f'Pre_ROI_{self.recipe}'][key].split(',')]
        for i in config[f'ID_{self.recipe}']:
            self.Class_Name_All.append(config[f'ID_{self.recipe}'][i])

        for key in config[f'ROI_{self.recipe}']:
            # 使用split()方法按逗號分隔字串並得到一個包含數字的清單
            number_list = config[f'ROI_{self.recipe}'][key].split(',')
            # 將每個元素轉換為浮點數
            y_start = int(number_list[1])
            y_stop = int(number_list[1])+int(number_list[3])
            x_start = int(number_list[0])
            x_stop = int(number_list[0])+int(number_list[2])
            self.ROI_List.append(ROI_Data([], y_start, y_stop, x_start, x_stop))
        for key in config['Camera_Setting']:
            self.Camera_Setting[key] = float(config['Camera_Setting'][key])
        print(f'self.Camera_Setting = {self.Camera_Setting}')

        self.engineer_mode_login_password = config['password']['password1']

    def recipe_change(self, recipe):
        print(f'Recipe {self.recipe} --> {recipe}')
        self.recipe = recipe
        self.MeasureSize_Area_dic.clear()
        self.MeasureSize_Approx_ArcLength_dic.clear()
        self.MeasureSize_dic.clear()
        self.MeasureSize_Approx_Area_dic.clear()
        self.NotValid_NumberOfVertices_dic.clear()
        self.NotValid_dic.clear()
        self.read_ini()
class ROI_Data:
    def __init__(self, image, y_start, y_stop, x_start, x_stop):
        self.Image = image
        self.Y_start = y_start
        self.Y_stop = y_stop
        self.X_start = x_start
        self.X_stop = x_stop
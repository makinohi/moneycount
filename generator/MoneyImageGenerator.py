import os
import cv2
import numpy as np
from numpy.random import *

class MoneyImageGenerator:

    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 800
    
    def __init__(self,money_image_directory_path, money_min_count=1, money_max_count=5):

        #紙幣、硬貨のイメージを読込
        money_image_list = []
        file_name_list = os.listdir(money_image_directory_path)
        for file_name in file_name_list:
            image = cv2.imread(os.path.join(money_image_directory_path, file_name))
            money_image_list.append(image)

        #メンバ変数に格納
        self._money_min_count = money_min_count
        self._money_max_count = money_max_count
        self._money_image_list = money_image_list

    def Generate(self,directory_path, image_count):

        #出力先ディレクトリが存在しない場合、作成する
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)

        #image_count数分画像を生成する
        for image_index in range(image_count):
            money_count = randint(self._money_min_count, self._money_max_count + 1)
            print(money_count)

            #画像イメージ格納用配列生成
            image = np.zeros((self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), np.uint8)
            image[::,::,::] = 255
            
            offset_x = 20
            offset_y = 50

            bbox_list = []

            #紙幣、硬貨を配置する
            for _ in range(money_count):
                money_index = randint(0,3)
                money_image = self._money_image_list[money_index]
                image[offset_y:money_image.shape[0]+offset_y,offset_x:money_image.shape[1]+offset_x,::] = money_image
                bbox_list.append({
                        'kind':money_index,
                        'xmin':offset_x,
                        'ymin':offset_y,
                        'xmax':money_image.shape[1]+offset_x,
                        'ymax':money_image.shape[0]+offset_y,
                        })
                offset_x = offset_x + money_image.shape[1] + 10

            #画像ファイル出力
            file_name = f'{image_index+1}.bmp'
            cv2.imwrite(os.path.join(directory_path,file_name), image)

            #XML出力
            content = f'<annotation><filename>{file_name}</filename><size><width>{self.IMAGE_WIDTH}</width><height>{self.IMAGE_HEIGHT}</height><depth>3</depth></size>'
            
            objects = []
            for bbox in bbox_list:
                content = content + '<object><name>{0}</name><bndbox><xmin>{1}</xmin><ymin>{2}</ymin><xmax>{3}</xmax><ymax>{4}</ymax></bndbox></object>'.format(bbox['kind'],bbox['xmin'],bbox['ymin'],bbox['xmax'],bbox['ymax'])
            content = content + '</annotation>'

            xml_file_name = f'{image_index+1}.xml'
            with open(os.path.join(directory_path,xml_file_name), 'w') as file:
                file.write(content)

if __name__ == '__main__':
    generator = MoneyImageGenerator('./money_image/')
    generator.Generate('./output/', 200)
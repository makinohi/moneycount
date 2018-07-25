import os
import cv2
import numpy as np
from numpy.random import *

class MoneyImageGenerator:
    
    IMAGE_WIDTH  = 500
    IMAGE_HEIGHT = 500
    BACK_IMAGE_FILE = "./source/DSC_4742.JPG"
    
    
    def __init__(self,money_image_directory_path, money_min_count=1, money_max_count=5):

        #紙幣、硬貨のイメージを読込
        money_image_list = []
        file_name_list = os.listdir(money_image_directory_path)
        for file_name in file_name_list:
            image = cv2.imread(os.path.join(money_image_directory_path, file_name))
            money_image_list.append({'name':file_name,
                                     'image':image
                                     })

        #メンバ変数に格納
        self._money_min_count = money_min_count
        self._money_max_count = money_max_count
        self._money_image_list = money_image_list

    def Generate(self,directory_path, image_count):

        #出力先ディレクトリが存在しない場合、作成する
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)

        sourceImage = cv2.imread(self.BACK_IMAGE_FILE, cv2.IMREAD_COLOR)

        #image_count数分画像を生成する
        for image_index in range(image_count):
            money_count = randint(self._money_min_count, self._money_max_count + 1)
            print(money_count)

            #画像イメージ格納用配列生成
            image = np.zeros((self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), np.uint8)
            image[::,::,::] = 255
            
            bbox_list = []
            outputInfo = []

            money_image_list = []
            
            # 硬貨出力数を決める
            for _ in range(money_count * 5):
                money_index = randint(0,len(self._money_image_list))
                money_image = self._money_image_list[money_index]  
                money_image_list.append(money_image)
                
            maxCount = len(money_image_list)
            
            #1枚目の出力ポジション
            position_x = randint(0,200)
            position_y = randint(0,200)
            
            lastPosition_x = 0
            
            rowHeightMax = 0
            
            for i in range(maxCount):                
                # X軸のオフセット
                offset_x = randint(20,200)  

                # 出力画像
                money_image = money_image_list[i]['image']
                     
                # 出力ポジション
                position_x = position_x + offset_x
                # 画像がはみ出す場合、次の行へ
                if position_x + offset_x + money_image.shape[1]  > self.IMAGE_WIDTH:
                    position_x = randint(20,200)
                    position_y = position_y + rowHeightMax + randint(0,100)
                    lastPosition_x = 0
                    rowHeightMax = 0
                
                # 行が画像範囲を超える場合
                if position_y  + money_image.shape[0] >self.IMAGE_HEIGHT:
                    # 画像貼り付け処理を終了
                    break

                # bboxの最小値                
                xmin = position_x
                         
                # 出力ポジションが、1個隣の画像の最大サイズより小さい場合
                if position_x <  lastPosition_x:
                    # 画像が重なっているため、bboxの最小値を変更する
                    xmin = lastPosition_x
                
                # 同行の画像最大サイズ（高さ）設定
                if rowHeightMax < money_image.shape[0]:
                    rowHeightMax = money_image.shape[0]

                outputInfo.append({
                        'ymin':position_y,
                        'ymax':position_y + money_image.shape[0],
                        'xmin':position_x,
                        'xmax':position_x + money_image.shape[1],
                        'image':money_image
                        })

                #image[position_y:position_y + money_image.shape[0],position_x:position_x + money_image.shape[1],::] = money_image
                bbox_list.append({
                        'kind':money_image_list[i]['name'],
                        'xmin':xmin,
                        'ymin':position_y,
                        'xmax':position_x + money_image.shape[1],
                        'ymax':position_y + money_image.shape[0],
                        })
                
                lastPosition_x = position_x + money_image.shape[1]
    
            image[0:self.IMAGE_HEIGHT,0:self.IMAGE_WIDTH,::] = cv2.resize(sourceImage,(self.IMAGE_WIDTH ,self.IMAGE_HEIGHT))
                         
            for info in reversed(outputInfo):
                image[info['ymin']:info['ymax'],info['xmin'] :info['xmax'],::] = info['image']

            #画像ファイル出力
            fileBaseName,ext = os.path.splitext( os.path.basename(self.BACK_IMAGE_FILE) )
            file_name = f'{fileBaseName}_{image_index+1}.bmp'

            #cv2.imwrite(os.path.join(directory_path,file_name), sourceImg)
            cv2.imwrite(os.path.join(directory_path,file_name), image)

            #XML出力
            content = f'<annotation><filename>{file_name}</filename><size><width>{self.IMAGE_WIDTH}</width><height>{self.IMAGE_HEIGHT}</height><depth>3</depth></size>'
            
            objects = []
            for bbox in bbox_list:
                content = content + '<objectValue><name>{0}</name><bndbox><xmin>{1}</xmin><ymin>{2}</ymin><xmax>{3}</xmax><ymax>{4}</ymax></bndbox></objectValue>'.format(bbox['kind'],bbox['xmin'],bbox['ymin'],bbox['xmax'],bbox['ymax'])
            content = content + '</annotation>'

            xml_file_name = f'{fileBaseName}_{image_index+1}.xml'
            with open(os.path.join(directory_path,xml_file_name), 'w') as file:
                file.write(content)
   

if __name__ == '__main__':
    generator = MoneyImageGenerator('./money_image/')
    generator.Generate('./output/', 10)
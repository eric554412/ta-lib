'''
第一堂課 :折線圖
'''
# import matplotlib.pyplot as plt

# # plt.style.use('ggplot')
# plt.xkcd()

# age_x = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]

# # Median Python Developer Salaries by Age

# py_dev_y = [45372, 48876, 53850, 57287, 63016,
#             65998, 70003, 70000, 71496, 75370, 83640]

# #畫圖
# # plt.plot(age_x, py_dev_y, color = '#5a7d9a', linewidth = 3, label = 'Python')
# plt.plot(age_x, py_dev_y, label = 'Python')

# # Median JavaScript Developer Salaries by Age
# js_dev_y = [37810, 43515, 46823, 49293, 53437,
#             56373, 62375, 66674, 68745, 68746, 74583]


# # plt.plot(age_x, js_dev_y, color = '#adad3b', linewidth = 3, label = 'Javascript' )
# plt.plot(age_x, js_dev_y, label = 'Javascript')

# # Median Developer Salaries by Age
# dev_y = [38496, 42000, 46752, 49320, 53200,
#          56000, 62316, 64928, 67317, 68748, 73752]

# #畫圖
# plt.plot(age_x, dev_y, color = '#444444', linestyle = '--', label = 'All Dev')


# plt.xlabel('Ages')
# plt.ylabel('Median Salary (USD)')
# plt.title('Median Salary (USD) by Age')

# #標記線
# plt.legend()

# #格線
# # plt.grid(True)

# #填充
# plt.tight_layout()

# #儲存圖片
# # plt.savefig('plot.png')


# #呈現
# plt.show()






# import matplotlib.pyplot as plt
# # Ages 18 to 55
# # plt.xkcd()
# ages_x = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
#           36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]


# py_dev_y = [20046, 17100, 20000, 24744, 30500, 37732, 41247, 45372, 48876, 53850, 57287, 63016, 65998, 70003, 70000, 71496, 75370, 83640, 84666,
#             84392, 78254, 85000, 87038, 91991, 100000, 94796, 97962, 93302, 99240, 102736, 112285, 100771, 104708, 108423, 101407, 112542, 122870, 120000]
# plt.plot(ages_x, py_dev_y, color = 'b', linewidth = 1, label = 'Python')


# js_dev_y = [16446, 16791, 18942, 21780, 25704, 29000, 34372, 37810, 43515, 46823, 49293, 53437, 56373, 62375, 66674, 68745, 68746, 74583, 79000,
#             78508, 79996, 80403, 83820, 88833, 91660, 87892, 96243, 90000, 99313, 91660, 102264, 100000, 100000, 91660, 99240, 108000, 105000, 104000]
# plt.plot(ages_x, js_dev_y, color = 'g', linewidth = 1, label = 'Javascript')

# dev_y = [17784, 16500, 18012, 20628, 25206, 30252, 34368, 38496, 42000, 46752, 49320, 53200, 56000, 62316, 64928, 67317, 68748, 73752, 77232,
#          78000, 78508, 79536, 82488, 88935, 90000, 90056, 95000, 90000, 91633, 91660, 98150, 98964, 100000, 98988, 100000, 108923, 105000, 103117]
# plt.plot(ages_x, dev_y, linewidth = 1, linestyle = '--', label = 'All dev')

# plt.title('Median Salary (USD) by Age')
# plt.xlabel('Ages')
# plt.ylabel('Median Salary (USD)')

# plt.legend()
# #格線
# plt.grid(True)
# #填充
# plt.tight_layout()

# plt.show()

'''
第二堂課: bar charts
'''
# import matplotlib.pyplot as plt
# import numpy as np
# import csv
# from collections import Counter
# import pandas as pd

# ages_x = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
# index_x = np.arange(len(ages_x)) #創建出一個list從1-10
# width = 0.25

# py_dev_y = [45372, 48876, 53850, 57287, 63016,
#             65998, 70003, 70000, 71496, 75370, 83640]

# plt.bar(index_x - width, py_dev_y, color = '#008fd5', width = width,label = 'Python')


# js_dev_y = [37810, 43515, 46823, 49293, 53437,
#             56373, 62375, 66674, 68745, 68746, 74583]
# plt.bar(index_x, js_dev_y, color = '#444444', width = width, label = 'Javascript')



# dev_y = [38496, 42000, 46752, 49320, 53200,
#          56000, 62316, 64928, 67317, 68748, 73752]
# plt.bar(index_x + width, dev_y, color = '#e5ae38', width = width, label = 'All Dev')


# plt.title('Median Salary (USD) by Age')
# plt.xlabel('Ages')
# plt.ylabel('Median Salary (USD)')
# plt.legend()
# plt.xticks(ticks = index_x, labels = ages_x)


# plt.show()



## 讀取csv: with open
# counter裡面要加list,為計算出現次數的一個函數

# with open('/Users/huyiming/Downloads/data.csv') as csv_file :
#     csv_reader = csv.DictReader(csv_file)
#     row = next(csv_reader) #next可以列印出第一個值
#     print(row['LanguagesWorkedWith'])
    
#     language_counter = Counter()
    
#     for row in csv_reader :
#         language_counter.update(row['LanguagesWorkedWith'].split(';'))

# language = []
# popluarity = []

# for item in language_counter.most_common(15):
#     language.append(item[0])
#     popluarity.append(item[1])

# language.reverse()
# popluarity.reverse()

# plt.barh(language, popluarity)
# plt.tight_layout()

# plt.title('Most Popular Languages')
# plt.xlabel('Number of People Who Use')

# plt.show()
    
 
 
#用pandas

# df = pd.read_csv('/Users/huyiming/Downloads/data.csv')

# languages_respone = df['LanguagesWorkedWith']

# language_counter = Counter()

# for respone in languages_respone :
#     language_counter.update(respone.split(';'))
    
# language = []
# popularity = []

# for row in language_counter.most_common(15) :
#     language.append(row[0])
#     popularity.append(row[1])

# language.reverse()
# popularity.reverse()

# plt.barh(language, popularity)

# plt.title('Most Popular Languages')
# plt.xlabel('Number of People Who Use')
# plt.tight_layout()

# plt.show()


'''
第三堂課(pie chart),最好少於五個
'''
import matplotlib.pyplot as plt

# slices = [120, 80, 30, 20]
# labels = ['Sixty', 'Forty', 'Extra1', 'Extra2']
# colors = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f']

# plt.pie(slices, labels = labels, colors = colors, wedgeprops = {'edgecolor':'black'})

# plt.title('My Awesome Pie Chart')

# plt.show()


# Colors:
# Blue = #008fd5
# Red = #fc4f30
# Yellow = #e5ae37
# Green = #6d904f

slices = [59219, 55466, 47544, 36443, 35917]
labels = ['JavaScript', 'HTML/CSS', 'SQL', 'Python', 'Java']
explode = [0, 0, 0, 0.1, 0] #將他分離出來

# autopct:顯示趴數 , wedgeprops: 分割線
plt.pie(slices, labels = labels, explode = explode, shadow = True, 
        startangle = 90, autopct = '%1.1f%%',
        wedgeprops = {'edgecolor':'black'})

plt.title('My Awesome Pie Chart')
plt.tight_layout()
plt.show()


'''
第四堂課:stack plot(累積折線圖):隨時間變化的累積趨勢
'''
# import matplotlib.pyplot as plt

# minutes = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# # player1 = [1, 2, 3, 3, 4, 4, 4, 4, 5]
# # player2 = [1, 1, 1, 1, 2, 2, 2, 3, 4]
# # player3 = [1, 1, 1, 2, 2, 2, 3, 3, 3]

# player1 = [8, 6, 5, 5, 4, 2, 1, 1, 0]
# player2 = [0, 1, 2, 2, 2, 4, 4, 4, 4]
# player3 = [0, 1, 1, 1, 2, 2, 3, 3, 4]

# colors = ['#6d904f', '#fc4f30', '#008fd5']

# labels = ['player1', 'player2', 'player3']

# plt.style.use('fivethirtyeight')

# plt.stackplot(minutes, player1, player2, player3, labels = labels, colors = colors)

# plt.title('My Awesome Stack Plot')

# plt.tight_layout()

# #label的位置
# plt.legend(loc = (0.07, 0.05))

# plt.show()

# Colors:
# Blue = #008fd5
# Red = #fc4f30
# Yellow = #e5ae37
# Green = #6d904f

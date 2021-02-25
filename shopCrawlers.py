# test
# prodList = ['LAVIN 浪凡 花漾公主女性淡香水 90ml TESTER','SAMSUNG三星Galaxy A71 5G 8G/128G 6.7吋智慧手機','健司 辻利抹茶奶茶沖泡飲 22g * 30包','Jo Malone 英國梨與小蒼蘭 香水 100ml','EBI ELIE SAAB 夢幻花嫁淡香精 TESTER 90ml',
# 'MONTBLANC 萬寶龍 海洋之心女性淡香水 30ml 試用品TESTER','豐力富 紐西蘭頂級純濃奶粉 2.6 公斤']

from modules import *

def main():
    os.chdir(os.path.dirname(__file__))
    logging.basicConfig(filename = 'logs/shopCrawlers.log', filemode = 'w', format = '%(levelname)s:%(message)s', level = logging.DEBUG)
    logNprint = printNlog = functools.partial(logNprint_Template, logging.getLogger())  # use root logger

    # if called from Python, use mock caller
    if __name__ == '__main__':
        # app = xw.apps.active
        # wb = xw.books.active
        # ws = xw.sheets.active
        wb = xw.Book('自動查最低價.xlsm')
        ws = wb.sheets[0]  # use the first sheet in workbook
        # wb.set_mock_caller()  # apparently not necessary
        pass
    else:  # __name__ == 'shopCrawlers'
        wb = xw.Book.caller()
        ws = wb.sheets.active

    logNprint('[%s] Mission Start!' % time.asctime())
    t1 = time.time()  # type:float

    color = set(ws['a14'].value.split(','))
    threeC = list(ws['a18'].value.split(','))
    prodList = getProdList(ws)

    # print params to see how fast the program starts up
    print("color = ", color)
    print("3C = ", threeC)

    ws['a1'].value = '抓取中...'
    # disablePrint()
    crawler_on_Ymall(prodList, ws, color, threeC)
    # crawler_on_Ybuy(prodList, ws, color, threeC)
    # crawler_on_momo(prodList, ws, color, threeC)
    # crawler_on_pchome(prodList, ws, color, threeC)  # 時有 Bug 時沒有
    # crawler_on_etmall(prodList, ws, color, threeC)
    # crawler_on_FP(prodList, ws, color, threeC)  # 時好時壞
    # enablePrint()

    ws['a1'].value = '抓好了'
    t2 = time.time()  # type:float
    logNprint('[%s] Mission Complete!' % time.asctime())
    logNprint('Time elapsed: %.3f' % (t2 - t1))

def test():
    # xw.serve()    # what is this? crashes Excel
    pass

if __name__ == '__main__':
    # executes when run from IDE, but not from Excel
    main()

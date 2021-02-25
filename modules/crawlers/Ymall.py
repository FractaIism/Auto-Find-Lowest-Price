from modules.libraries import *
from modules.globals import *
from modules.utilities import *

def process_prod_Ymall(prod, index):
    # stash away logs and console messages in a 2-D list to prevent race conditions
    log_stash = []
    print_stash = []
    # shorthand functions, usage: stashLog(str[,str,...])
    stashLog = functools.partial(stashLog_Template, log_stash)  # write to log file
    stashPrint = functools.partial(stashLog_Template, print_stash)  # print to console
    stashLogPrint = lambda msg, *args: [stashLog(msg, *args), stashPrint(msg, *args)]  # output to both console and log file
    # object to pass as return value
    retObj = {
        "data"  : ('?', '?', '?'),  # type:tuple
        "logs"  : log_stash,  # type:list
        "prints": print_stash,  # type:list
    }

    # ws['a1'].value = 'Y城：{0}/{1}'.format(j, len(prod_list))  # no longer needed because multithreading makes searching fast af boi
    try:
        stashLogPrint('搜尋商品：%s' % re.sub('___', ' ', prod))
        names = []
        urls = []
        prices = []

        req = session.get(Ym_url, params = {
            'p'   : re.sub('___', ' ', prod),
            'qt'  : 'product',
            'sort': 'p'
        }, headers = headers)
        req.encoding = 'utf-8'
        # stashLog(req.url)

        # 以 Beautiful Soup 解析 HTML 程式碼
        soup = bs(req.text, 'html.parser')

        # a container encompassing all candidate products
        gridList = soup.find('ul', class_ = 'gridList')
        if gridList is None:
            stashLogPrint("無任何搜尋結果")
            # stashLogPrint('=' * 35)
            retObj["data"] = ('-', '-', '-')
            return retObj

        # ----- 抓取搜尋結果網頁上的品名、價格、網址 ------
        found_names = found_prices = found_urls = []  # silence the IDE nagging about using variables before assignment
        try:
            found_names = [x.string for x in gridList.find_all('span', class_ = 'BaseGridItem__title___2HWui')]
            found_prices = [x.string[1:] for x in gridList.find_all('em')]  # do NOT include class_, sometimes it does not have a class
            found_urls = [li.a['href'] for li in gridList.find_all('li', class_ = 'BaseGridItem__grid___2wuJ7')]
        except TypeError as typerr:  # type 轉換時的錯誤預防
            stashLog(typerr)
            for li in soup.find('ul', class_ = 'gridList').find_all('li'):
                stashLog("搜尋到的商品列表：\n", li.text)

        # if any of the results returned an empty list, the website has changed and source code requires updating
        if [] in (found_names, found_prices, found_urls):
            stashLog('Search XXX: 抓到的商品名稱或價格或網址為空。目標網站結構可能有變，原始碼需要修改')
            stashLog('抓到商品名稱：%a' % found_names)
            stashLog('抓到商品價格：%a' % found_prices)
            stashLog('抓到商品網址：%a' % found_urls)
            stashPrint('目標網頁結構可能有變，沒有抓到目標名稱或網址或價格')
            stashPrint('跳過 Y城 的搜尋') # no need to stop when multithreading
            retObj["data"] = tuple([r'¯\_(ツ)_/¯'] * 3)
            return retObj

        # 過濾並儲存相符品名
        for i in range(len(found_names)):
            if is_same_prod(prod, found_names[i], color, threeC):
                stashLogPrint('相似品名：%s' % found_names[i])
                names.append(found_names[i])
                prices.append(found_prices[i])
                urls.append(found_urls[i])

        # stashLog("0x9487", prices)
        prices = removeComma_and_toInt(prices)

        if len(names) == 0:
            stashLogPrint('無相符之搜尋結果')
            # stashLogPrint('=' * 35)
            retObj["data"] = tuple(['-'] * 3)
            return retObj
        else:
            stashLogPrint('抓到相符商品數：%d' % len(names))
            stashLog('抓到商品：%a' % names)

        # 將資料存入以待寫入
        min_price_index = prices.index(min(prices))
        # stashPrint('=' * 35)
        retObj["data"] = (prices[min_price_index], names[min_price_index], urls[min_price_index])
        return retObj
    except Exception:
        stashLog(traceback.format_exc())
        retObj["data"] = tuple(['X'] * 3)
        return retObj

def crawler_on_Ymall(prod_list: list, ws, color_, threeC_):
    """抓取 Yahoo!超級商城 上的最低價"""
    # logger to write to Ymall.log
    logger = getModuleLogger(__name__)
    logger.info('Crawl on Ymall')
    # utility function to log and print in one line (make an alias in case I forget if it's logNprint or printNlog...)
    logNprint = printNlog = functools.partial(logNprint_Template, logger)

    # 印分隔線
    logNprint('*' * 15 + ' Yahoo!超級商城 ' + '*' * 15)
    # make parameters available to each task thread
    global color, threeC
    (color, threeC) = (color_, threeC_)
    global Ym_url, session
    Ym_url = 'https://tw.search.mall.yahoo.com/search/mall/product?'
    # todo: why use session here?
    session = requests.session()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prod_Ymall, prod, index) for (index, prod) in enumerate(prod_list)]
        results = [future.result() for future in futures]

    # results: list of retObj
    for idx, res in enumerate(results):
        logNprint("=" * 35)
        print(f"Product #{idx}: {res['data']}")
        for line in res["logs"]:
            logger.info(line)
        for line in res["prints"]:
            print(line)
    logNprint("=" * 35)

    # 輸出至Excel的資料，格式: (最低價,商品名稱,網址)
    # result_for_write = [('-', '-', '-') for j in range(len(prod_list))]
    result_for_write = [retObj["data"] for retObj in results]
    # 將資料寫入儲存格
    ws['c3'].value = result_for_write
    logNprint('Yahoo!超級商城 抓取完畢！\n\n')

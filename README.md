# 抓取 steam 商店游戏信息
利用 scrapy 抓取 [steam](http://store.steampowered.com/) 游戏平台所有上线发布的游戏信息，并存入数据库。

### 项目依赖库
* scrapy
* mysql-connector-python [安装参考](http://stackoverflow.com/questions/31748278/how-do-you-install-mysql-connector-python-development-version-through-pip) 
* BeautifulSoup
* lxml

### 抓取流程
1. [将 steam 所有游戏](http://store.steampowered.com/search) 按照发布时间逆序排序，共能够看到截止 2017-3-6 steam 上共有 24483 个游戏。
2. 提取所有游戏的链接、名称、所在页数、是否已经抓取状态存入数据库。
3. 请求第二步中得到的游戏的 url，获取响应后的页面，然后提取游戏的相关信息。

### 抓取过程中遇到的问题
* 年龄验证，steam 平台上有一些游戏有年龄限制，不是所有的年龄都能够访问。所以在访问的过程中有时出现一个临时页面要求验证年龄。查看浏览器网络请求发现是一个 post 请求。所以解决方法就是在一个年龄段内随机挑选一个然后模拟 post 请求。请求参数 ageDay, ageMobth, ageYear, snr.
* 类型请求：steam 还有一些游戏可能不适合在工作时或者所有年龄段浏览。中间也会有一个临时的页面需要点击确认。查看网页源码发现点击之后会执行一个 js 的方法，并且执行后会添加一个 cookie 设置 mature_content=1。所以这里有两种解决方法
	* 利用 selenium 模拟鼠标点击按钮，然后在请求相应连接
	* 在浏览器中找到确认后的 cookie 在访问开始时，添加到请求中
由于不想引入 selenium 库，所以这里采用第二种方式。 	

### 关于 steam 游戏 id
steam 的 url 一般为 http://store.steampowered.com/app/620/ 这是 [Protal 2](http://store.steampowered.com/app/620/) 游戏的链接。所以在看是的时候以为每一个游戏都有一个对应的 id。例如 Portal 2  就是 620 。但在实际抓取中总发现，抓取到的 url 数量总是比 24483 少两百多个。经过仔细研究对比终于找到原因。

有一些游戏在初期会发布免费的 demo 试玩版，收集用户数据，然后对游戏进行更改。游戏正式上线后，之前的 demo 版就可能失效了，或者直接跳转到正式版的链接。这就变成了一个游戏，只存在了同一个 id。但是在所有游戏排行中，却显示为两个游戏。所以会出现抓取到的数量会比实际显示数量少两百多的情况。折腾了许久，以此记录。

### 下载运行

```
$ git clone https://github.com/awolfly9/steam.git
```

进入游戏目录

```
$ cd steam
```

修改数据库配置

```
$ vim config.py
------------
database_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
}
```

编辑 main.py 先抓取 url

```
$ vim main.py
---------
cmdline.execute('scrapy crawl game_urls'.split())
# cmdline.execute('scrapy crawl game_info'.split())
```

运行爬虫抓取 url 信息

```
$ python main.py
```

待 urls 抓取完成后再抓取游戏信息

```
$ vim main.py
---------
# cmdline.execute('scrapy crawl game_urls'.split())
cmdline.execute('scrapy crawl game_info'.split())
```
运行爬虫抓取游戏信息

```
$ python main.py
```






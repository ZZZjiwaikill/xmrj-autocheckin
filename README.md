# 校猫日记自动打卡脚本

这是一个用于完成"校猫日记"微信小程序打卡的Python脚本。

## 功能特点

- 自动获取当前积分、服务器时间戳，仅需要抓包获取1次个人Token，一劳永逸
- 按照设定规则，每日定时定点自动打卡
- 每日只打卡一次的限制（可取消）
- 一次运行，多人打卡

## 安装使用

1. 克隆项目并配置py包`requests`
   ```bash
   git clone https://github.com/ZZZjiwaikill/xmrj-autocheckin.git
   cd xmrj-autocheckin
   pip install requests
   ```
2. 使用Charles进行抓包后，填写`config.py`文件。具体步骤如下：
   1. 根据[Charles使用教程（一）| 使用Charles抓包微信小程序](https://www.zhihu.com/tardis/bd/art/1896701961547538943)，安装软件、根证书
   2. 停止录制，清空所有抓包记录，尽可能地关闭浏览器以确保没有或只有少量其他请求在进行。
   3. 抓包：
      1. 开始录制
      2. 点击“我要签到”按钮，抓包软件会记录下这个请求。
      3. 停止录制
      4. 查看抓包记录，如下图找到`config.py`内待填写的信息：![alt text](ref_image.jpg)
   4. 在 `config.py` 中，填写你的个人信息
3. 走你:
   ```bash
   python xmrj_autocheckin.py
   ```
   若命令行输出为
   ```bash
   打卡结果： {'points': {'ID': xxx, 'Mobile': xxx, 'BeforePoints': 120, 'ProcessPoints': 10, 'AfterPoints': 130, 'CreateTime': xxx, 'Reason': '签到'}}
   打卡成功，已记录
   --- done ---
   ```
   则说明已打卡成功~ 此时python脚本已测试完成，恭喜你获得了10分！就差最后一步啦——
4. 自动化设置：
   1. 将`xmrj_autostart.bat`中的`cd`命令更改为你自己的该项目路径。注意：如果路径在不同的盘符下，例如我的路径在D盘，需要加上 /d 参数
   2. 将`xmrj_autostart.bat`添加到Windows任务计划程序中，设置为每天定时执行。具体如下：
      1. 按 Win+R，输入 taskschd.msc
      2. 创建基本任务
      3. 名称: "校猫日记自动打卡"（可自定义）
      4. 触发器: "计算机启动时"
      5. 操作: "启动程序"，选择`xmrj_autostart.bat`文件
      6. 条件: 取消"只有在计算机使用交流电源时才启动此任务"
      7. 设置: 选中"如果任务已运行，则不要启动新实例"
      8. 设置完成后，双击你创建的任务：![alt text](set_image.png)*PS：可以右键单击任务，选择运行以测试效果*
      9. “触发器”-“新建”，可新建自定义规则（例如每天8点执行），这样计算机就会按照你的自定义规则以自动运行脚本啦！
      10. 记得点击“确定”以保存退出~

## 重要声明

本脚本仅用于教育和技术研究目的。请注意：

1. 请勿滥用打卡功能
2. 使用本脚本即表示您同意仅用于合法目的。
3. 脚本已内置每日一次的限制机制
4. 请勿在`config.py`文件中取消每日打卡的限制！（`ENABLE_DAILY_CHECKIN_LIMIT = False`）否则将会导致一天之内重复打卡，重复领取积分！

## 免责声明

作者不对使用此脚本可能造成的任何问题负责，请合理使用。

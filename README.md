# SDN_research

声明：

本教程仅为个人研究、技术研究目的而创作及分享，内容聚焦于网络安全防御原理、漏洞分析思路、合法渗透测试流程等基础技术知识，旨在帮助使用者提升网络安全认知与防御能力，而非传授非法攻击手段。
使用者承诺：获取本教程后，仅可在已获得明确授权的合法网络环境中进行技术验证，严禁将教程内容用于任何未经授权的商业活动、破坏他人网络系统、窃取数据、侵犯隐私等违法违规行为，亦不得将教程内容传播给任何用于非法目的的第三方。
使用者需在下载本教程后的 24 小时内，自行删除教程的所有副本，逾期保留或继续使用均视为违反本声明，由此产生的一切责任由使用者自行承担。

本文仅供参考，你所做的一切行为与一切后果皆与作者无关

本文建议读者拥有的知识水平：知晓Linux基础，用过Linux shell，会用搜索引擎与ai解决问题

关键词：上海电信SDN，telnet，shell

感谢列表：
恩山老哥@焉知祸福 https://www.right.com.cn/forum/thread-4058319-1-1.html 分享的全包固件
https://github.com/yangfl/HG2821T-U_SDN 分享的解包后固件，没有这二位提供的固件，就没有后续的分析

前情提要：
https://www.right.com.cn/forum/thread-8438800-1-1.html
https://www.right.com.cn/forum/thread-8441736-1-1.html

本文同步于GitHub ： https://github.com/haoqi366/SDN_research
后续提取的信息也将同步在GitHub上更新与存储

—————————————正文开始—————————————————————
本人光猫是XE-140W-TD，软件版本NBEL.2.0.4，但是考虑到SDN光猫平台的相似性，可以合理推断本研究在大部分光猫适用
[图片：光猫网页信息]



通过感谢列表里的老哥提取的固件，发现在http://[光猫ip]/config/drstrange/处存在shell注入漏洞
通过构建访问“http://[光猫ip]/config/drstrange/;[command]”即可执行[command]内容，这是接下来的基础

但是直接通过浏览器这样进行注册存在着一定问题，
一是空格会自动被编码为“%20”，在执行时无法被正常解析，
二是‘/’字符会直接被服务器截断，导致无法正常直接访问文件系统
三是只有部分命令有回显(后经过验证，发现是只显示stderr输出)

以下是解决方案：
通过环境变量${IFS}与${HOME}，可以分别解决问题一与二，只不过普通浏览器无法正常传输含“{}”的数据，所以需要自己编写程序，实现不编码的http请求，我直接找ai写了一个
针对问题三，可以通过执行类似“mkdir $([command])”的命令，将command正常回显输出利用mkdir的报错进行返回，从而得到输出
但是这样的输出有着较多限制，可以在初步获取shell权限后，用别的方法替代
[sdn.py]

这样便可以获得shell执行权限，但这个shell肯定不好用，我们需要telnet来获取更好用的shell
注意！！！请确保你的sdn光猫没有开启Wi-Fi，Wi-Fi功能可能会导致tcp连接不稳定（鬼知道为什么，被这个问题坑了一周）
这个时候，我们可以弄一个busybox，进而利用busybox的telnetd功能
前往[busybox下载页面](https://www.busybox.net/downloads/binaries/1.26.2-defconfig-multiarch/)下载对应架构的busybox，然后传输到光猫
怎么传输：光猫自带了tftp，ftpget，curl，u盘默认挂载点为/mnt/usb1_1（有概率挂载不上，需要手动mount）,具体的去问百度或者ai，这里不展开

可以将自己的busybox放在/usr/local/或者/tmp，记得chmod 777授权，然后执行"/path/to/busybox telnetd -l /bin/sh"（一定要记得用绝对路径！）启动telnet

注意：
如果curl一直无法建立连接，或者telnetd服务开启后无法连接，可能是ovs配置导致的，有2个解决方案：
一：杀掉httpd进程，然后将telnetd端口指定为80，"/path/to/busybox telnetd -l /bin/sh -p 80"，对应telnet连接时用80端口（仅针对telnetd无法连接）
二：执行ovs-vsctl set-fail-mode SDN-bridge standalone，在我的设备上，这就能正常建立tcp连接，但可能有隐藏的问题，我还没有发现

这样用telnet即可建立对光猫shell的访问，enjoy！


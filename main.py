"""
这是一个下载爱奇艺教育频道资源的脚本，第一版本主要关注解析和批量下载的实现。后续可能会增加批量展示可下载内容和上传至Google Drive的功能。
感谢Dannikuaile提供的接口
使用nilaoda的N_m3u8DL-CLI工具进行下载，在此表示感谢
"""
import time
import os
import codecs
import hashlib
import requests

class QiyiVideo(object):
    def __init__(self, url):
        self.url = url

    @staticmethod
    def standard(name):
        '''标准化文件及文件夹的命名'''
        nm = name.replace("|", "：").replace(":", "：").replace("?", "？").replace("/", "").replace("\\", "").replace("*", "")
        nm = nm.replace("<", "《").replace(">", "》").replace('"', "“")
        return nm

    def autodl(self):
        self.url2aid()
        self.aid2tvid()
        if os.path.exists(self.title):
            pass
        else:
            os.mkdir(self.title)
        for video in self.videos:
            m3uname = self.tvid2m3u8(video["id"], video["pd"])
            self.download(m3uname, video["subTitle"])

    def url2aid(self):
        """
        通过url获得视频aid
        """
        headers = {
            'Accept - Encoding': "gzip",
            'User - Agent': "Mozilla / 5.0(Macintosh; Intel Mac OS X 10_11_6) AppleWebKit \
                            / 537.36(KHTML, like Gecko) Chrome / 53.0.2785.143 Safari / 537.36",
            'qyid': "0_a80059e64bc3a81f_F4Z91Z1EZ07ZFAZ42",
            't': "466931948",
            'sign': "ffe061391e40c6a4ec7d1368c0333032"
        }
        params = {
            'app_k': "20168006319fc9e201facfbd7c2278b7",
            'app_v': "8.9.5",
            'platform_id': "10",
            'dev_os': "8.0.1",
            'dev_ua': "Android",
            'net_sts': "1",
            'qyid': "9900077801666C",
            'secure_p': "GPhone",
            'secure_v': "1",
            'dev_hw': "%7B%22cpu%22:0,%22gpu%22:%22%22,%22mem%22:%22%22%7D",
            'app_t': "0",
            'h5_url': self.url
        }
        get_url = "http://iface2.iqiyi.com/video/3.0/v_play"
        r = requests.get(get_url, params=params, headers=headers, timeout=30).json()
        self.aid = r["play_aid"]
        self.title = self.standard(r["album"]["_t"])

    def aid2tvid(self):
        """
        通过aid获取视频tvid列表
        """
        headers = {
            'User - Agent': "Mozilla / 5.0(Macintosh; Intel Mac OS X 10_11_6) AppleWebKit \
                                    / 537.36(KHTML, like Gecko) Chrome / 53.0.2785.143 Safari / 537.36"
        }
        params = {
            'albumId': self.aid,
            'size': 500,
            'page': 1,
            'needPrevue': "True",
            'needVipPrevue': "false",
        }
        get_url = "https://pub.m.iqiyi.com/h5/main/videoList/album/"
        r = requests.get(get_url, params=params, headers=headers, timeout=30).json()
        self.videos = r["data"]["videos"]

    def tvid2m3u8(self, tvid, chapter):
        """
        由视频id产生m3u8文件
        :param tvid: 视频id
        """
        headers = {
            'User - Agent': "Mozilla / 5.0(Macintosh; Intel Mac OS X 10_11_6) AppleWebKit \
                                            / 537.36(KHTML, like Gecko) Chrome / 53.0.2785.143 Safari / 537.36"
        }
        timestamp = str(int(time.time()*1000))
        #接口隐藏
        get_url = "https://cache.video.iqiyi.com"
        print(get_url+param)
        r = requests.get(get_url+param, headers=headers, timeout=30).json()
        #寻找清晰度最高的版本
        maxindex = 0
        for index, res in enumerate(r["data"]["vp"]["tkl"][0]["vs"]):
            if index > 1:
                if res["vsize"] > r["data"]["vp"]["tkl"][0]["vs"][maxindex]["vsize"]:
                    maxindex = index
        #构造m3u8文件
        m3u8 = "#EXTM3U\n#EXT-X-TARGETDURATION:300\n"
        for clip in r["data"]["vp"]["tkl"][0]["vs"][maxindex]["fs"]:
            m3u8 += "#EXTINF:400\n"
            cdn = "http://data.video.iqiyi.com/videos" + clip["l"]
            down = requests.get(cdn, headers=headers, timeout=30).json()["l"]
            m3u8 += down + "\n"
        m3u8 += "#EXT-X-ENDLIST\n\n"
        with codecs.open("%02d.m3u8" % chapter, "a+", "utf-8") as f:
            f.write(m3u8)
        return "%02d.m3u8" % chapter

    def download(self, mname, oname):
        """
        调用工具下载文件
        :param mname: m3u8文件名
        :param oname: 输出文件名
        :return:
        """
        cfg = {
            "tool": "N_m3u8DL-CLI_v2.3.0.exe",
            "workdir": self.title,
            "savename": oname
        }
        task = cfg["tool"]+ " \""+ mname+ "\" --workDir \""+ cfg["workdir"]+ "\" --saveName \""+oname +"\" --enableDelAfterDone"
        os.system(task)
        os.remove(mname)

if __name__ == "__main__":
    url = input("请输入你要下载的教育资源链接，形如http://www.iqiyi.com/v_19rrd0u0vw.html：")
    a = QiyiVideo(url)
    a.autodl()

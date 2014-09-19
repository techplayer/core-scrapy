#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 一些工具类
Desc : 
"""
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os.path
from scrapydemo.settings import IMAGES_STORE


def filter_tags(htmlstr):
    """更深层次的过滤，类似instapaper或者readitlater这种服务，很有意思的研究课题
    过滤HTML中的标签
    将HTML中标签等信息去掉
    @param htmlstr HTML字符串.
    """
    # 先过滤CDATA
    re_pp = re.compile('</p>', re.I)  # 段落结尾
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_br = re.compile('<br\s*?/?>')  # 处理换行
    re_h = re.compile('</?\w+[^>]*>')  # HTML标签
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释

    s = re_pp.sub('\n', htmlstr)  # 段落结尾变换行符
    s = re_cdata.sub('', s)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    # 去掉多余的空行
    blank_line = re.compile('\n+')
    s = blank_line.sub('\n', s)
    s = replace_charentity(s)  # 替换实体
    return "".join([t.strip() + '\n' for t in s.split('\n') if t.strip() != ''])


def replace_charentity(htmlstr):
    """
    ##替换常用HTML字符实体.
    #使用正常的字符替换HTML中特殊的字符实体.
    #你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    #@param htmlstr HTML字符串.
    """
    char_entities = {'nbsp': ' ', '160': ' ',
                     'lt': '<', '60': '<',
                     'gt': '>', '62': '>',
                     'amp': '&', '38': '&',
                     'quot': '"', '34': '"', }

    re_charentity = re.compile(r'&#?(?P<name>\w+);')
    sz = re_charentity.search(htmlstr)
    while sz:
        entity = sz.group()  # entity全称，如&gt;
        key = sz.group('name')  # 去除&;后entity,如&gt;为gt
        try:
            htmlstr = re_charentity.sub(char_entities[key], htmlstr, 1)
            sz = re_charentity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charentity.sub('', htmlstr, 1)
            sz = re_charentity.search(htmlstr)
    return htmlstr


def repalce(s, re_exp, repl_string):
    return re_exp.sub(repl_string, s)


def ltos(lst):
    """列表取第一个值"""
    if lst is not None and isinstance(lst, list):
        if len(lst) > 0:
            return lst[0]
    return ''


def send_mail(jokes):
    sender = 'xiongneng@gzhdi.com'
    receiver = ['xiongneng@gzhdi.com', '']
    subject = '糗事百科最新笑话-祝你开心每一天'
    smtpserver = 'smtp.263.net'
    username = 'xiongneng@gzhdi.com'
    password = '620817'
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = subject

    msg_text_str = """
        <h1>糗事百科，祝君笑口常开。</h1>
        <div class="listbox">
            <ul>
        """
    for idx, (content, img_url) in enumerate(jokes, 1):
        msg_text_str = "\n".join([msg_text_str, '<li>'])
        msg_text_str = "\n".join([msg_text_str, '<p>%s</p>' % content])
        if img_url:
            msg_text_str = "\n".join([msg_text_str, '<p><img src="cid:image%s"/></p>' % idx])
        msg_text_str = "\n".join([msg_text_str, '</li>'])
    msg_text_str = "\n".join([msg_text_str, '</ul>'])
    msg_text_str = "\n".join([msg_text_str, '</div>'])

    msg_text = MIMEText(msg_text_str, 'html', 'utf-8')
    msg_root.attach(msg_text)

    for idx, (_, img_url) in enumerate(jokes, 1):
        if img_url:
            with open(os.path.join(IMAGES_STORE, os.path.basename(img_url)), 'rb') as fp:
                msg_image = MIMEImage(fp.read())
                msg_image.add_header('Content-ID', '<image%s>' % idx)
                msg_root.attach(msg_image)
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg_root.as_string())
    smtp.quit()


if __name__ == '__main__':
    print('呜呜呜仍无法发干撒发斯蒂芬,\nadfasdfsa')
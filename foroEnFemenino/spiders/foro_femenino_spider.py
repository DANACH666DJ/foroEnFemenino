# -*- coding: utf-8 -*-
import scrapy
import sys
import urlparse
from foroEnFemenino.items import ForoenfemeninoItem


class foroEnFemenino(scrapy.Spider):
    name = "enFemenino"
    allowed_domains = ["enfemenino.com"]
    custom_settings = {"SCHEDULER_DISK_QUEUE": 'scrapy.squeues.PickleFifoDiskQueue',
                       "SCHEDULER_MEMORY_QUEUE": 'scrapy.squeues.FifoMemoryQueue'}

    # constructor
    def __init__(self, *a, **kw):
        super(foroEnFemenino, self).__init__(*a, **kw)
        reload(sys)
        sys.setdefaultencoding("utf-8")

    # método que inicializa la url principal y la manda al método parse
    def start_requests(self):
        urls = 'http://foro.enfemenino.com/foro/'
        yield scrapy.Request(url=urls, callback=self.parse)

    # recibo la url del tema y empiezo el crawl
    def parse(self, response):
        # creo un xpath que recorre todos los titulos , textos  y url de cada tema
        forum_url = response.xpath('//div[@class="forum"][3]//a[@class="forum-link"]/@href').extract_first()
        forum_title = response.xpath('//div[@class="forum"][3]//a[@class="forum-link"]/text()').extract_first()
        # creo un meta para ir insertando nuestros datos
        meta = {'forum_url': forum_url,
                'forum_title': forum_title
                }
        yield scrapy.Request(forum_url, callback=self.parse_urlsPagAsuntos, meta=meta)

    # método que lee cada url del método parse y la recorre para extraer subject_title y  subject_user(se le manda por meta los datos de parse)
    def parse_urlsPagAsuntos(self, response):
        # recibo  el meta
        meta = response.meta
        # creo un xpath que recorre todos los titulos de asuntos ,nombre de users que han creado el post y la url del post
        items = response.xpath('//div[@class="af-thread-item"]')
        for article in items:
            subject_url = article.xpath('.//a/@href').extract_first()
            subject_title = article.xpath('.//a//span[@class="thread-title"]/text()').extract_first()
            subject_user = article.xpath('.//a//div[@class="user-name"]/text()').extract()[0].strip()
            subject_user = str(subject_user)
            subject_user = subject_user.replace("por: ", "")
            subject_num_answer = article.xpath(
                './/a//div[@class="right-zone"]//span[@class="nb-responses-desktop"]/text()').extract_first()
            subject_date_last_post = article.xpath(
                './/a//div[@class="right-zone"]//div[@class="af-label last-answer"]//span/text()').extract()[
                0].strip()
            # le añado al meta que recibo mas datos
            meta['subject_url'] = subject_url
            meta['subject_title'] = subject_title
            meta['subject_user'] = subject_user
            meta['subject_num_answer'] = subject_num_answer
            meta['subject_date_last_post'] = subject_date_last_post
            if subject_url == "http://salud.enfemenino.com/foro/nuevas-fotos-aumento-a-los-7-dias-submuscular-390cc-fd984676":
                yield scrapy.Request(subject_url, callback=self.parse_urlsPagPost, meta=meta)


        # paginación de la página de asuntos
        next_page = response.xpath('//nav[@class="af-pagination "]//li[@class="selected"]/following-sibling::li/a/@href').extract_first()
        if not next_page is None:
            yield scrapy.Request(next_page, callback=self.parse_urlsPagAsuntos, meta=response.meta)


    def parse_urlsPagPost(self, response):
        # recibo los datos del  meta
        meta = response.meta
        post_title = response.xpath('//div[@class="af-post-title"]/h1/a/text()').extract_first()
        # puesto que solo hay una pregunta en cada post,cogo el user de la pregunta,el texto y la fecha
        post_user_question = response.xpath(
            '//div[@class="af-post first"]//span[@class="user-name-value"]/text()').extract_first()
        post_date_question = response.xpath(
            '//div[@class="af-post first"]//span[@class="date"]/text()').extract_first().strip()
        post_text_question = response.xpath('//div[@class="af-post first"]//p[@class="af-message"]/text()').extract()
        # cogemos el texto y lo metemos como parametro al metodo clean para que nos deje solo el texto sin espacios
        post_text_question = self.clean_and_flatten(post_text_question)
        # cast de post_text a string ,puesto que necesitamos transformarlo a utf-8
        post_text_question = str(post_text_question)
        # transformo el post_text a utf8
        post_text_question = unicode(post_text_question, "utf-8")
        # le añado al meta que recibo mas datos
        meta['post_title'] = post_title
        meta['post_user_question'] = post_user_question
        meta['post_date_question'] = post_date_question
        meta['post_text_question'] = post_text_question
        meta['post_user_answer'] = None
        meta['post_date_answer'] = None
        meta['post_text_answer'] = None

        meta['user_question_sex'] = None
        meta['user_question_age'] = None
        meta['user_question_location'] = None
        meta['user_question_name'] = None
        meta['user_question_surname'] = None

        meta['user_answer_sex'] = None
        meta['user_answer_age'] = None
        meta['user_answer_location'] = None
        meta['user_answer_name'] = None
        meta['user_answer_surname'] = None

        # si no tiene respuestas lo creo sólo con la preguntas
        url_user_question = urlparse.urljoin("http://www.enfemenino.com/mi-espacio/", post_user_question)
        meta['url_user_question'] = url_user_question
        yield scrapy.Request(url_user_question, callback=self.parse_user, meta=meta, dont_filter=True)

        # creo un xpath que recorre todos los userPost,totalMesUser,date,post_group,post_member_group y textPost
        items = response.xpath('//div[@class="af-post"]')
        # si hay respuestas a la pregunta la creamos
        if items is not None:
            for article in items:
                post_user_answer = article.xpath(
                    './/div[@class="af-post-header"]//span[@class="user-name-value"]/text()').extract_first()
                post_date_answer = article.xpath(
                    './/div[@class="af-post-header"]//span[@class="date"]/text()').extract_first().strip()
                post_text_answer = article.xpath(
                    './/div[@class="af-post-message"]/p[@class="af-message"]/text()').extract()
                # cogemos el texto y lo metemos como parametro al metodo clean para que nos deje solo el texto sin espacios
                post_text_answer = self.clean_and_flatten(post_text_answer)
                # cast de post_text_answer a string ,puesto que necesitamos transformarlo a utf-8
                post_text_answer = str(post_text_answer)
                # transformo el post_text_answer a utf8
                post_text_answer = unicode(post_text_answer, "utf-8")
                # le añado al meta que recibo mas datos
                meta['post_user_answer'] = post_user_answer
                meta['post_date_answer'] = post_date_answer
                meta['post_text_answer'] = post_text_answer

                # antes estaba con el post user question y funcionaba(sin el meta )
                url_user_answer = urlparse.urljoin("http://www.enfemenino.com/mi-espacio/", post_user_answer)
                yield scrapy.Request(url_user_answer, callback=self.parse_user_answer, meta=meta, dont_filter=True)

        # paginación de la página de asuntos
        next_page = response.xpath(
            '//nav[@class="af-pagination light next-button"]//li[@class="selected"]/following-sibling::li/a/@href').extract_first()
        if not next_page is None:
            print "*****************", next_page
            yield scrapy.Request(next_page, callback=self.parse_urlsPagPost, meta=response.meta)

    # PRUEBAAAAAA METODO
    def parse_user_answer(self, response):
        meta = response.meta
        url_user_question = meta['url_user_question']
        # si recibo la url del user answer creo sus datos(esto no estaba cuando funcionaba)
        for nodes in response.xpath('//table[1]//td/font[@class="afmod_contentB"]'):
            nombre = nodes.xpath('text()').extract()
            nombre = str(nombre[0])
            # transformo el nombre a utf8
            nombre = unicode(nombre, "utf-8")
            if nombre == "Sexo":
                user_answer_sex = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_answer_sex'] = user_answer_sex
            if nombre == "Nombre":
                user_answer_name = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_answer_name'] = user_answer_name
            if nombre == "Apellidos":
                user_answer_surname = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_answer_surname'] = user_answer_surname
            if nombre == "Edad":
                user_answer_age = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_answer_age'] = user_answer_age
            if nombre == "Lugar":
                user_answer_location = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract()
                if not user_answer_location == []:
                    meta['user_answer_location'] = user_answer_location
        yield scrapy.Request(url_user_question, callback=self.parse_user, meta=meta, dont_filter=True)

    def parse_user(self, response):
        # recibo los datos
        meta = response.meta
        for nodes in response.xpath('//table[1]//td/font[@class="afmod_contentB"]'):
            nombre = nodes.xpath('text()').extract()
            nombre = str(nombre[0])
            # transformo el nombre a utf8
            nombre = unicode(nombre, "utf-8")
            if nombre == "Sexo":
                user_question_sex = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_question_sex'] = user_question_sex
            if nombre == "Nombre":
                user_question_name = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_question_name'] = user_question_name
            if nombre == "Apellidos":
                user_question_surname = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_question_surname'] = user_question_surname
            if nombre == "Edad":
                user_question_age = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract_first()
                meta['user_question_age'] = user_question_age
            if nombre == "Lugar":
                user_question_location = nodes.xpath(
                    '../following-sibling::td//a[@class="afmod_content"]/text()').extract()
                if not user_question_location == []:
                    meta['user_question_location'] = user_question_location

        yield self.create_item(meta)

    def clean_and_flatten(self, text_list):
        clean_text = []
        for text_str in text_list:
            if text_str == None:
                continue
            if len(text_str.strip()) > 0:
                clean_text.append(text_str.strip())

        return "\n".join(clean_text).strip()

        # método para armar el item con los datos que hemos ido añadiendo al meta

    def create_item(self, meta):
        item = ForoenfemeninoItem()
        item['forum_url'] = meta['forum_url']
        item['forum_title'] = meta['forum_title']
        item['subject_url'] = meta['subject_url']
        item['subject_user'] = meta['subject_user']
        item['subject_title'] = meta['subject_title']
        item['subject_num_answer'] = meta['subject_num_answer']
        item['subject_date_last_post'] = meta['subject_date_last_post']
        item['post_title'] = meta['post_title']
        item['post_user_question'] = meta['post_user_question']
        item['post_date_question'] = meta['post_date_question']
        item['post_text_question'] = meta['post_text_question']
        item['post_user_answer'] = meta['post_user_answer']
        item['post_date_answer'] = meta['post_date_answer']
        item['post_text_answer'] = meta['post_text_answer']
        item['user_question_sex'] = meta['user_question_sex']
        item['user_question_name'] = meta['user_question_name']
        item['user_question_surname'] = meta['user_question_surname']
        item['user_question_age'] = meta['user_question_age']
        item['user_question_location'] = meta['user_question_location']
        # esto no estaba cuando funcionaba
        item['user_answer_sex'] = meta['user_answer_sex']
        item['user_answer_name'] = meta['user_answer_name']
        item['user_answer_surname'] = meta['user_answer_surname']
        item['user_answer_age'] = meta['user_answer_age']
        item['user_answer_location'] = meta['user_answer_location']
        return item

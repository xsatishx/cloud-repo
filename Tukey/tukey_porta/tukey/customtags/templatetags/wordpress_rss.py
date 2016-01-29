import re

import feedparser

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

# use_wordpress = True
use_wordpress = False

register = template.Library()

import cgi, string

# convert text to html (for use with rss content)
# https://djangosnippets.org/snippets/19/
re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp|https)://.*?))(\s|$)', re.S|re.M|re.I)
def plaintext2html(text, tabstop=4):
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;'*tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' '*tabstop;
        else:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
    return re.sub(re_string, do_sub, text)


@register.tag(name='wordpress_rss')
def do_rss_latest(parser, token):
    """
    A template tag to grab the latest articles from a given feed.
    The first argument is the category.
    The second argument is the number of items to retrieve.
    The third argument (after 'as') is the variable to store the result in.
    """

    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires three arguments:"
            + "category, number of items to retrieve and a variable name"
            % token.contents.split()[0]
        )
    m = re.search(r'(.*?) ([0-9]+) as (\w+)', args)

    if not m:
        raise template.TemplateSyntaxError(
            "%r has invalid arguments" % tag_name
        )

    category, num_items, var_name = m.groups()

    try:
        number_of_items = int(num_items)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r's second argument must be a number" % tag_name
        )

    return GetRSSLatest(category, number_of_items, var_name)

class GetRSSLatest(template.Node):
    def __init__(self, category, number_of_items, var_name):
        self.category = template.Variable(category)
        self.number_of_items = number_of_items
        self.var_name = var_name

    def render(self, context):
        try:
            actual_category = self.category.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.var_name] = []

        if use_wordpress:
            base_url = getattr(
                settings,
                'WORDPRESS_RSS_BASE_URL', 
                'http://news.opensciencedatacloud.org'
                )
        else:
            base_url = getattr(
                settings,
                'WORDPRESS_RSS_BASE_URL', 
                'http://occ-data.org'
                )
            
        feed_url = base_url + '/feed/'


        if actual_category is not None:
            feed_url += '/category/'
            feed_url += str(actual_category)
        
        d = feedparser.parse(feed_url)

        for item in d.entries[:self.number_of_items]:

            try:
                # Use the wordpress feed entries
                if use_wordpress:
                    publish_datetime = item['published_parsed']

                    rss_item = {
                        'title': item.title_detail['value'],
                        'href': item.link,
                        'content': mark_safe(item.content[0]['value']),
                        'published': "%s/%s/%s" % 
                        (publish_datetime[0], publish_datetime[1], publish_datetime[2]),
                        'author': item.author
                        }
                    
                # Use rss feed entries
                else:

                    published = " ".join(item['published'].split()[:4])
                    
                    N_CONTENT_LINES = 10

                    # format the content and add images
                    content = item.summary.splitlines()
                    content = ' '.join(content[:N_CONTENT_LINES])
                    content = plaintext2html(content)
                    url = item.title_detail                    
                    if isinstance(url, basestring) and url != "":
                        if "http" not in url:
                            url = base_url + url
                        style = "max-height: 170px; max-width: 190px; float:left; margin: 0px;"
                        style += "padding-right: 15px; "
                        image = """<img style='%s' src='%s'>""" % (style, url)
                        content = image+content
                    content += """<a href="%s"><b> ... more ...</b></a>""" % item.id
                    
                    rss_item = {
                        'title': item.title,
                        'href': item.id,
                        'content': mark_safe(content),
                        'published': published,
                        }
                
                context[self.var_name].append(rss_item)

            except AttributeError:
                pass
            except:
                print "Unexpected error:", sys.exc_info()[0]
        return ''

